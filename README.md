# 🚀 Cobble Downloader

**Software experimental** para baixar vídeos e áudios diretamente do navegador, usando Python (FastAPI) e yt-dlp.  
Ainda em **versão primordial**, sujeito a erros e melhorias futuras.

---

## 📦 Pré-requisitos

- Python 3.11 ou superior  
- pip instalado  

---

## 🛠️ Passo a passo

### 1. Clone o repositório

```bash
git clone https://github.com/LRaposoRocha/cobble.git
cd cobble
```

### 2. Instale as dependências

```bash
pip install fastapi uvicorn yt-dlp
```

### 3. Inicie a API

```bash
python -m uvicorn cobble_API:app --reload
```

### 4. Abra a interface

```bash
cobble_Code.html
```

---

## ✨ Melhorias futuras

- Barra de progresso visual enquanto baixa  
- Melhor tratamento de erros  
- Otimização para dispositivos móveis  
- Personalização de formatos de saída  
- Suporte a múltiplos downloads simultâneos  

---

## 📄 Licença

Este projeto está sob a **Licença MIT**.
