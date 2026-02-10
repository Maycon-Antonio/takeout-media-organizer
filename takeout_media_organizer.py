import os
import json
import shutil
import subprocess
import csv
from datetime import datetime, timezone

# ================= CONFIGURAÇÕES =================
PASTA_ORIGEM  = r"C:\Users\mayco\Downloads\MidiaBruta_GoogleFotos_Takeout"
PASTA_DESTINO = r"C:\Users\mayco\Downloads\Organizado_GoogleFotos_Takeout"
RELATORIO_CSV = r"C:\Users\mayco\Downloads\Relatorio_GoogleFotos_Takeout.csv"

EXT_FOTOS  = [".jpg", ".jpeg", ".png", ".webp", ".heic"]
EXT_VIDEOS = [".mp4", ".mov", ".avi", ".mkv"]

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}
# =================================================


def run_exiftool(args):
    subprocess.run(
        ["exiftool"] + args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False
    )


def encontrar_json(pasta, nome_arquivo):
    """
    Encontra o JSON correspondente ao arquivo de mídia
    usando slice para contornar o limite de nome do Takeout.
    """
    nome_base = nome_arquivo.lower()[:40]

    for f in os.listdir(pasta):
        f_lower = f.lower()
        if f_lower.startswith(nome_base) and f_lower.endswith(".json"):
            return os.path.join(pasta, f)

    return None


def nome_unico(destino, nome_arquivo):
    """
    Garante que o nome do arquivo não sobrescreva outro existente.
    """
    base, ext = os.path.splitext(nome_arquivo)
    contador = 1
    novo_nome = nome_arquivo

    while os.path.exists(os.path.join(destino, novo_nome)):
        novo_nome = f"{base}_{contador}{ext}"
        contador += 1

    return novo_nome


def processar():
    arquivos_processados = set()  # evita duplicidade no relatório

    with open(RELATORIO_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Caminho original",
            "Caminho final",
            "Tipo",
            "Data recuperada",
            "Ano",
            "Mês",
            "Dia",
            "GPS recuperado",
            "Status"
        ])

        for root, _, files in os.walk(PASTA_ORIGEM):
            for file in files:
                caminho_arquivo = os.path.join(root, file)

                if caminho_arquivo in arquivos_processados:
                    continue

                nome, ext = os.path.splitext(file)
                ext = ext.lower()

                if ext not in EXT_FOTOS + EXT_VIDEOS:
                    continue

                arquivos_processados.add(caminho_arquivo)

                json_path = encontrar_json(root, file)

                if not json_path:
                    writer.writerow([
                        caminho_arquivo, "", ext, "", "", "", "", "Não", "JSON não encontrado"
                    ])
                    continue

                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    writer.writerow([
                        caminho_arquivo, "", ext, "", "", "", "", "Não", "Erro ao ler JSON"
                    ])
                    continue

                # ===== DATA REAL =====
                ts = None
                if "photoTakenTime" in data and "timestamp" in data["photoTakenTime"]:
                    ts = int(data["photoTakenTime"]["timestamp"])
                elif "creationTime" in data and "timestamp" in data["creationTime"]:
                    ts = int(data["creationTime"]["timestamp"])

                if not ts:
                    writer.writerow([
                        caminho_arquivo, "", ext, "", "", "", "", "Não", "Sem data válida"
                    ])
                    continue

                dt = datetime.fromtimestamp(ts, tz=timezone.utc)

                ano = dt.year
                mes = dt.month
                dia = dt.day
                mes_nome = MESES[mes]

                # ===== NOME PELO TITLE =====
                novo_nome = data.get("title", file).strip()

                # Remove caracteres inválidos no Windows
                for c in r'<>:"/\|?*':
                    novo_nome = novo_nome.replace(c, "_")

                if not os.path.splitext(novo_nome)[1]:
                    novo_nome += ext

                # ===== PASTA FINAL =====
                pasta_final = os.path.join(
                    PASTA_DESTINO,
                    str(ano),
                    f"{mes:02d} - {mes_nome}",
                    f"{dia:02d}"
                )
                os.makedirs(pasta_final, exist_ok=True)

                novo_nome = nome_unico(pasta_final, novo_nome)
                novo_caminho = os.path.join(pasta_final, novo_nome)

                # ===== METADADOS =====
                data_str = dt.strftime("%Y:%m:%d %H:%M:%S")

                run_exiftool([
                    "-overwrite_original",
                    f"-DateTimeOriginal={data_str}",
                    f"-CreateDate={data_str}",
                    f"-ModifyDate={data_str}",
                    caminho_arquivo
                ])

                gps_ok = "Não"
                geo = data.get("geoData", {})
                lat = geo.get("latitude", 0.0)
                lon = geo.get("longitude", 0.0)

                if lat != 0.0 and lon != 0.0:
                    run_exiftool([
                        "-overwrite_original",
                        f"-GPSLatitude={lat}",
                        f"-GPSLongitude={lon}",
                        caminho_arquivo
                    ])
                    gps_ok = "Sim"

                # ===== MOVER ARQUIVO =====
                shutil.move(caminho_arquivo, novo_caminho)

                # ===== REMOVER JSON =====
                try:
                    os.remove(json_path)
                except Exception:
                    pass

                writer.writerow([
                    caminho_arquivo,
                    novo_caminho,
                    "Foto" if ext in EXT_FOTOS else "Vídeo",
                    dt.isoformat(),
                    ano,
                    mes_nome,
                    dia,
                    gps_ok,
                    "OK"
                ])

                print(f"✅ {file} → {novo_caminho}")


if __name__ == "__main__":
    processar()
