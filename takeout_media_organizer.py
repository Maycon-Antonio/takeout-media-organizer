import os
import json
import shutil
import subprocess
import csv
from datetime import datetime, timezone

# ================= CONFIGURAÇÕES =================
PASTA_ORIGEM  = os.path.join(os.path.dirname(__file__), "data", "media_raw")
PASTA_DESTINO = os.path.join(os.path.dirname(__file__), "data", "media_organized")
RELATORIO_CSV = os.path.join(os.path.dirname(__file__), "reports", "processing_report.csv")
EXIFTOOL_PATH = os.path.join(os.path.dirname(__file__), "exiftool", "exiftool.exe")

EXT_FOTOS  = [".jpg", ".jpeg", ".png", ".webp", ".heic"]
EXT_VIDEOS = [".mp4", ".mov", ".avi", ".mkv"]

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}
# =================================================


def run_exiftool(args):
    cmd = [EXIFTOOL_PATH] + args
    subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False
    )


def encontrar_json(pasta, nome_arquivo):
    """
    Encontra JSON do Google Takeout mesmo que o nome esteja truncado
    Ex:
    - .supplemental-metadata.json
    - .supplemental-metadata-me
    - .supplemental-metadata-ma
    """
    nome_base = nome_arquivo.lower()

    for f in os.listdir(pasta):
        f_lower = f.lower()
        if (
            f_lower.startswith(nome_base)
            and "supplemental-metadata" in f_lower
        ):
            return os.path.join(pasta, f)

    return None


def processar():
    with open(RELATORIO_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Arquivo original",
            "Arquivo final",
            "Tipo",
            "Data recuperada",
            "Ano",
            "Mes",
            "Dia",
            "GPS recuperado",
            "Status"
        ])

        for root, dirs, files in os.walk(PASTA_ORIGEM):
            for file in files:
                nome, ext = os.path.splitext(file)
                ext = ext.lower()

                if ext not in EXT_FOTOS + EXT_VIDEOS:
                    continue

                caminho_arquivo = os.path.join(root, file)
                json_path = encontrar_json(root, file)

                if not json_path:
                    writer.writerow([
                        file, "", ext, "", "", "", "", "Não", "JSON não encontrado"
                    ])
                    continue

                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except:
                    writer.writerow([
                        file, "", ext, "", "", "", "", "Não", "Erro ao ler JSON"
                    ])
                    continue

                # ===== DATA REAL =====
                if "photoTakenTime" in data and "timestamp" in data["photoTakenTime"]:
                    ts = int(data["photoTakenTime"]["timestamp"])
                elif "creationTime" in data and "timestamp" in data["creationTime"]:
                    ts = int(data["creationTime"]["timestamp"])
                else:
                    writer.writerow([
                        file, "", ext, "", "", "", "", "Não", "Sem data válida"
                    ])
                    continue

                dt = datetime.fromtimestamp(ts, tz=timezone.utc)

                ano = dt.year
                mes = dt.month
                dia = dt.day
                mes_nome = MESES[mes]

                # ===== NOME PELO TITLE =====
                novo_nome = data.get("title", file)
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

                # ===== REMOVER JSON APÓS SUCESSO =====
                try:
                    os.remove(json_path)
                except:
                    pass

                writer.writerow([
                    file,
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
