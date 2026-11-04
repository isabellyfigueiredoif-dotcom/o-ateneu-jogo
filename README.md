# O Ateneu — jogo online

## Publicar na internet
1. Crie um repositório no GitHub.
2. Envie os arquivos desta pasta para o repositório. Não renomeie `app.py`.
3. No Render, crie um **Web Service** e conecte o repositório.
4. Use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --workers 1 --threads 8 --timeout 120 app:app`
5. Aguarde a publicação. O Render fornecerá um endereço público HTTPS.
6. Abra o endereço, crie uma sala e envie o link e o código aos participantes.

O arquivo `render.yaml` já contém a configuração de implantação.

## Como funciona
- Apresentador cria a sala e controla as etapas.
- Cada participante entra pelo navegador do próprio celular, tablet ou computador.
- O placar é atualizado automaticamente.
- Cada resposta correta vale 10 pontos.
- O jogo tem quatro etapas e perguntas sobre *O Ateneu*.

## Limitações importantes
Esta versão guarda as partidas na memória do processo do servidor. É adequada para uma atividade escolar curta, mas a sala será perdida se o servidor reiniciar ou o serviço for republicado. Não reinicie o serviço durante a partida. O plano gratuito pode demorar para iniciar após um período sem uso; abra e teste o endereço antes da apresentação.

O site não está publicado ainda. Este pacote contém o projeto pronto para você enviar ao GitHub e hospedar no Render. Não compartilhe dados pessoais dos participantes; use primeiro nome ou apelido.
