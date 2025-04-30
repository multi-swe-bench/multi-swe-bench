FROM ubuntu:latest



WORKDIR /home/

RUN apt update && apt install -y git nodejs npm && npm install -g pnpm@8

RUN git clone https://github.com/sveltejs/svelte.git /home/svelte

CMD ["pnpm", "playwright", "install", "chromium"]



