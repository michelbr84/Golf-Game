# 📂 Super Minigolf - Estrutura do Projeto

Este documento descreve a estrutura completa de pastas e arquivos do jogo, incluindo detalhes sobre cada asset.

---

## 🗂️ Árvore de Diretórios

```
Golf-Game/
│
├── 📄 main.py                    # Arquivo principal do jogo (1217 linhas)
├── 📄 physics.py                 # Sistema de física e cálculos de trajetória
├── 📄 courses.py                 # Definição dos 9 níveis/buracos
├── 📄 startScreen.py             # Tela inicial, menu e loja
├── 📄 get_pip.py                 # Script para instalação automática de pip
│
├── 📄 scores.txt                 # Salvamento de pontuações e moedas
├── 📄 README.md                  # Documentação principal
├── 📄 ToDo.md                    # Tracker de features e melhorias
├── 📄 structure.md               # Este arquivo
│
├── 📄 .gitpod.dockerfile         # Configuração Docker para Gitpod
├── 📄 .gitpod.yml                # Configuração do workspace Gitpod
│
├── 📁 img/                       # Assets visuais (sprites e imagens)
│   └── (23 arquivos - detalhes abaixo)
│
├── 📁 sounds/                    # Assets de áudio
│   └── (5 arquivos - detalhes abaixo)
│
└── 📁 __pycache__/               # Cache do Python (gerado automaticamente)
    └── (arquivos .pyc compilados)
```

---

## 📜 Arquivos Python

### `main.py` (49.2 KB - 1217 linhas)
Arquivo principal contendo:
- Loop principal do jogo
- Sistema de renderização (redrawWindow)
- Sistema de colisão
- Lógica de power-ups
- Sistema de áudio
- Classe `scoreSheet` (placar)
- Funções de gameplay (fade, showScore, holeInOne, etc.)

### `physics.py` (857 bytes)
Módulo de física contendo:
- Cálculos de trajetória parabólica
- Função `ballPath()` - posição da bola ao longo do tempo
- Função `maxTime()` - tempo máximo de voo

### `courses.py` (5.7 KB)
Definição dos níveis:
- 9 níveis com configurações únicas
- Posições de spawn da bola
- Posições dos buracos/bandeiras
- Obstáculos por nível (água, areia, laser, paredes)
- Sistema de moedas por nível
- Valores de par por buraco

### `startScreen.py` (8.9 KB)
Tela inicial e sistema de loja:
- Classe `ball` - representação de bolas na loja
- Função `mainScreen()` - renderiza menu principal
- Função `drawShop()` - renderiza interface da loja
- Sistema de compra e equipamento

### `get_pip.py` (1.7 MB)
Script standalone para instalação do pip caso não esteja disponível.

---

## 🖼️ Assets de Imagem (`img/`)

### Backgrounds e Cenário

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `back.png` | 205 KB | Fundo principal do jogo (céu + montanhas + vegetação) |
| `course1.png` | 229 KB | Thumbnail do curso para menu de seleção |
| `title.png` | 57 KB | Logo "Super Minigolf" para tela inicial |

### Elementos de Gameplay

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `flag.png` | 386 B | Sprite da bandeira/buraco |
| `green.png` | 123 B | Textura do green (área de putt) |
| `power.png` | 38 KB | Medidor de força no canto inferior |

### Obstáculos

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `sand.png` | 618 B | Textura de areia (hazard) |
| `sandEdge.png` | 126 B | Borda lateral da areia |
| `sandBottom.png` | 114 B | Borda inferior da areia |
| `water.png` | 141 B | Textura de água (hazard) |
| `laser.png` | 102 B | Obstáculo laser (hazard) |
| `sticky.png` | 132 B | Superfície adesiva (para Sticky Ball) |

### Animação de Moedas (8 frames)

| Arquivo | Tamanho | Frame |
|---------|---------|-------|
| `coin1.png` | 293 B | Frame 1 |
| `coin2.png` | 344 B | Frame 2 |
| `coin3.png` | 346 B | Frame 3 |
| `coin4.png` | 384 B | Frame 4 |
| `coin5.png` | 361 B | Frame 5 |
| `coin6.png` | 332 B | Frame 6 |
| `coin7.png` | 308 B | Frame 7 |
| `coin8.png` | 259 B | Frame 8 |

### Ícones

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `icon.png` | 3.3 KB | Ícone do jogo (PNG) |
| `icon.ico` | 90 KB | Ícone do jogo (Windows ICO) |

### Sistema

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `Thumbs.db` | 209 KB | Cache de miniaturas do Windows (pode ser ignorado) |

---

## 🔊 Assets de Áudio (`sounds/`)

| Arquivo | Tamanho | Duração | Descrição |
|---------|---------|---------|-----------|
| `music.mp3` | 6.1 MB | ~4 min | Música de fundo em loop |
| `putt.wav` | 265 KB | ~1.5s | Som de tacada |
| `inHole.wav` | 159 KB | ~0.9s | Som ao acertar o buraco |
| `splash.wav` | 110 KB | ~0.6s | Som ao cair na água |
| `wrong12.wav` | 25 KB | ~0.3s | Som de erro/power-up indisponível |

---

## 💾 Arquivos de Dados

### `scores.txt`
Arquivo de texto para persistência de dados do jogador:
```
score [pontuação]
coins [quantidade_de_moedas]
[cor_rgb]-[status_desbloqueado]
...
```

Exemplo:
```
score 32
coins 45
255,255,255-True
255,0,0-True
0,255,0-False
...
```

---

## ⚙️ Arquivos de Configuração

### `.gitpod.yml`
Configuração do Gitpod para desenvolvimento online:
- Define tasks de inicialização
- Configura porta do servidor

### `.gitpod.dockerfile`
Dockerfile personalizado para o ambiente Gitpod.

---

## 📊 Resumo de Assets

| Categoria | Quantidade | Tamanho Total |
|-----------|------------|---------------|
| Imagens | 22 arquivos | ~625 KB |
| Áudio | 5 arquivos | ~6.7 MB |
| Python | 4 arquivos | ~60 KB |
| **Total** | **31 arquivos** | **~7.4 MB** |

---

## 🎨 Detalhes Técnicos dos Assets

### Imagens
- **Formato**: PNG (com transparência onde necessário)
- **Resolução do jogo**: 1080 x 600 pixels
- **Background**: 1280 x 720 pixels (renderizado com offset)

### Áudio
- **Música**: MP3 (compressão lossy)
- **Efeitos**: WAV (sem compressão para menor latência)
- **Sample rate**: Padrão (44.1 kHz)

### Animações
- **Moedas**: 8 frames, ~15 ticks por frame
- **Fade**: Transição alpha incremental

---

*Última atualização: Janeiro 2026*
