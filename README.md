# Google Fotos Takeout Organizer

Script em **Python** para organizar backups do **Google Fotos (Google Takeout)**, restaurando metadados originais, renomeando arquivos corretamente e organizando fotos e vídeos de forma cronológica e definitiva.

---

## 📌 Funcionalidades

* Percorre **todas as pastas** do Google Takeout
* Consolida **todas as fotos e vídeos** em uma pasta de mídia bruta
* Associa corretamente arquivos `.json` às mídias
* Restaura **metadados EXIF completos**:

  * Data e hora original da captura
  * Data de criação e modificação
  * Localização GPS (quando disponível)
* Renomeia arquivos usando o **título presente no JSON**
* Organiza automaticamente em estrutura cronológica:

  ```
  Ano/
    Mês/
      Dia/
        arquivos.jpg / arquivos.mp4
  ```
* Remove arquivos processados da pasta original
* Remove JSON após aplicação bem-sucedida
* Gera **relatório CSV detalhado** do processamento
* Trata casos especiais:

  * JSON truncado (`ME`, `metadata`, `supplemental-metadata`)
  * Arquivos ocultos no Windows
  * Datas ausentes ou inválidas

---

## 🧠 Motivação

Ao exportar dados do Google Fotos:

* As imagens **perdem metadados**
* Datas ficam incorretas
* Arquivos vêm com nomes aleatórios
* Organização por álbuns não é confiável

Este script reconstrói o **arquivo histórico pessoal de fotos e vídeos**, mantendo fidelidade total aos dados originais.

---

## 📂 Estrutura do Projeto

```
takeout-media-organizer/
│
├── src/                  ← scripts Python
│   └── takeout_media_organizer.py
│
├── data/
│   ├── takeout_raw/      ← Takeout extraído (ZIP → extrair aqui)
│   ├── media_raw/        ← mídia bruta unificada (JPG, MP4, etc)
│   └── media_organized/  ← resultado final organizado
│
├── reports/
│   └── takeout_report.csv
│
├── README.md
├── LICENSE
└── requirements.txt
```

---

## ⚙️ Requisitos

* Python **3.10 ou superior**
* Sistema operacional: Windows, Linux ou macOS
* Biblioteca externa:

  * `exiftool` (obrigatório)

### Instalação do ExifTool (Windows)

1. Baixe em: [https://exiftool.org](https://exiftool.org)
2. Extraia o conteúdo na raiz do projeto
3. Renomeie a pasta e o arquivo executável para exiftool
4. Teste no terminal:

   ```
   exiftool -ver
   ```

---

## ▶️ Como Usar

1. Extraia **todos os ZIPs do Google Takeout** em data\takeout_raw
2. Mova todas as mídias diretamente para data\media_raw
3. Execute o script:

   ```
   python takeout-media-organizer.py
   ```
4. Aguarde o processamento
5. Verifique o arquivo `processing_report.csv`
6. Ao final, aproveite os dados organizados em data\media_organized

---

## 🧾 Relatório de Processamento

O script gera automaticamente um relatório contendo:

* Nome original do arquivo
* Nome final
* Caminho final
* Tipo (foto/vídeo)
* Data usada
* Status do processamento
* Erros encontrados (se houver)

Esse relatório serve como **auditoria e validação técnica**.

---

## 📱 Uso em Android (Sem Aparecer na Galeria)

Para armazenar as mídias no celular **sem aparecer na galeria** e **sem backup automático**:

1. Copie a pasta organizada para o celular
2. Crie um arquivo vazio chamado:

   ```
   .nomedia
   ```
3. Coloque esse arquivo dentro da pasta principal

---

## ⚠️ Observações Importantes

* O script **não apaga arquivos em caso de erro**
* JSON só é removido após aplicação correta dos metadados
* Arquivos sem data válida são separados para análise manual
* Recomenda-se manter um backup adicional em HD externo

---

## 📈 Melhorias Futuras (Roadmap)

* Interface gráfica (GUI)
* Suporte a HEIC
* Logs em formato JSON
* Paralelização para grandes volumes
* Modo dry-run (simulação)

---

## 📄 Licença

Este projeto está licenciado sob a licença **MIT**.  
Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Autor

**Maycon Antonio Aguiar Santos**
Técnico em Informática
Estudante de Ciência da Computação
