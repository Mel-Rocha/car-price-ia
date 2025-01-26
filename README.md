# Rodando o projeto ⚙️

0. Abra o notebook no google colab e explore o código.
1. Crie o arquivo .env com as variáveis de ambiente.
2. Crie o ambiente virtual e ative-o.
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Instale as dependências.
```bash
pip install -r requirements.txt
```
### Rodar localmente
4. Rode o projeto 
```bash
uvicorn main:app --reload
```
5. Acesse o projeto na porta.
```bash
http://127.0.0.1:8000/docs#/
```
### Rodar no Docker
4. Rode o projeto 
```bash
docker compose up --build
```
5. Acesse o projeto na porta.
```bash
http://0.0.0.0:8086/docs#/

```
----
## Formatadores e Linters 💎

- Para aplicar recursivamente as correções de estilo PEP8 a todos os arquivos no diretório atual:
```bash
autopep8 --in-place --aggressive --aggressive --recursive .
```

## Variaveis de ambiente 📝 
```bash
SECRET_KEY="your-secure-secret-key"
AUTH_TOKEN="your-secure-auth-token"

```

