import pygame
import random
import time
import os
import json

# Configurações do jogo
LARGURA_TELA = 800
ALTURA_TELA = 600
TAMANHO_CELULA = 40
LINHAS = ALTURA_TELA // TAMANHO_CELULA
COLUNAS = LARGURA_TELA // TAMANHO_CELULA

CORES = {
    'fundo': (220, 220, 255),
    'parede': (60, 60, 120),
    'caminho': (255, 255, 255),
    'gato': (200, 100, 100),
    'queijo': (255, 220, 80),
    'texto': (30, 30, 30),
}

ARQUIVO_RECORDE = 'recorde.json'

pygame.init()
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption('Labirinto: Gato e Queijo')
fonte = pygame.font.SysFont('Arial', 28)
relogio = pygame.time.Clock()

# Sons (opcional)
def carregar_som(nome):
    try:
        return pygame.mixer.Sound(nome)
    except:
        return None

som_vitoria = carregar_som('vitoria.wav')
som_passos = carregar_som('passo.wav')

# Sprites simples (pode substituir por imagens)
# Carregar imagem do gato
try:
    img_gato = pygame.image.load(os.path.join('assets', 'gato.png'))
    img_gato = pygame.transform.scale(img_gato, (TAMANHO_CELULA, TAMANHO_CELULA))
except:
    img_gato = None

# Carregar imagem do queijo
try:
    img_queijo = pygame.image.load(os.path.join('assets', 'queijo.png'))
    img_queijo = pygame.transform.scale(img_queijo, (TAMANHO_CELULA, TAMANHO_CELULA))
except:
    img_queijo = None

def desenhar_gato(x, y):
    if img_gato:
        tela.blit(img_gato, (x, y))
    else:
        pygame.draw.ellipse(tela, CORES['gato'], (x+5, y+10, TAMANHO_CELULA-10, TAMANHO_CELULA-20))
        pygame.draw.circle(tela, (0,0,0), (x+TAMANHO_CELULA//2, y+TAMANHO_CELULA//2), 5)

def desenhar_queijo(x, y):
    if img_queijo:
        tela.blit(img_queijo, (x, y))
    else:
        pygame.draw.polygon(tela, CORES['queijo'], [
            (x+TAMANHO_CELULA//2, y+10),
            (x+TAMANHO_CELULA-10, y+TAMANHO_CELULA-10),
            (x+10, y+TAMANHO_CELULA-10)
        ])
        pygame.draw.circle(tela, (200, 180, 40), (x+TAMANHO_CELULA//2, y+TAMANHO_CELULA//2), 5)

# Geração de labirinto (DFS)
def gerar_labirinto(linhas, colunas):
    lab = [[1 for _ in range(colunas)] for _ in range(linhas)]
    stack = []
    x, y = 0, 0
    lab[y][x] = 0
    stack.append((x, y))
    dx = [0, 1, 0, -1]
    dy = [-1, 0, 1, 0]
    while stack:
        x, y = stack[-1]
        vizinhos = []
        for d in range(4):
            nx, ny = x + dx[d]*2, y + dy[d]*2
            if 0 <= nx < colunas and 0 <= ny < linhas and lab[ny][nx] == 1:
                vizinhos.append((nx, ny, d))
        if vizinhos:
            nx, ny, d = random.choice(vizinhos)
            lab[y+dy[d]][x+dx[d]] = 0
            lab[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    return lab

def encontrar_posicao_vazia(lab):
    while True:
        x = random.randint(0, COLUNAS-1)
        y = random.randint(0, LINHAS-1)
        if lab[y][x] == 0:
            return x, y

def salvar_recorde(tempo):
    try:
        with open(ARQUIVO_RECORDE, 'w') as f:
            json.dump({'recorde': tempo}, f)
    except:
        pass

def carregar_recorde():
    if not os.path.exists(ARQUIVO_RECORDE):
        return None
    try:
        with open(ARQUIVO_RECORDE, 'r') as f:
            data = json.load(f)
            return data.get('recorde')
    except:
        return None

def desenhar_labirinto(lab):
    for y in range(LINHAS):
        for x in range(COLUNAS):
            cor = CORES['parede'] if lab[y][x] == 1 else CORES['caminho']
            pygame.draw.rect(tela, cor, (x*TAMANHO_CELULA, y*TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))

def main():
    dificuldade = 'medio'  # fácil, medio, dificil
    if dificuldade == 'facil':
        linhas, colunas = 10, 15
    elif dificuldade == 'dificil':
        linhas, colunas = 20, 30
    else:
        linhas, colunas = LINHAS, COLUNAS

    labirinto = gerar_labirinto(linhas, colunas)
    pos_gato = encontrar_posicao_vazia(labirinto)
    pos_queijo = encontrar_posicao_vazia(labirinto)
    while pos_queijo == pos_gato:
        pos_queijo = encontrar_posicao_vazia(labirinto)

    tempo_inicio = time.time()
    tempo_final = None
    recorde = carregar_recorde()
    venceu = False
    rodando = True

    direcao = None
    tempo_ultimo_passo = 0
    intervalo_passo = 80  # milissegundos entre passos

    while rodando:
        tela.fill(CORES['fundo'])
        desenhar_labirinto(labirinto)
        xg, yg = pos_gato
        xq, yq = pos_queijo
        desenhar_queijo(xq*TAMANHO_CELULA, yq*TAMANHO_CELULA)
        desenhar_gato(xg*TAMANHO_CELULA, yg*TAMANHO_CELULA)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    main()
                    return
                if venceu:
                    continue
        # Detectar teclas pressionadas
        if not venceu:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1
            if (dx != 0 or dy != 0) and pygame.time.get_ticks() - tempo_ultimo_passo > intervalo_passo:
                nx, ny = xg + dx, yg + dy
                if 0 <= nx < colunas and 0 <= ny < linhas and labirinto[ny][nx] == 0:
                    pos_gato = (nx, ny)
                    if som_passos: som_passos.play()
                    tempo_ultimo_passo = pygame.time.get_ticks()

        if not venceu and pos_gato == pos_queijo:
            tempo_final = time.time() - tempo_inicio
            venceu = True
            if som_vitoria: som_vitoria.play()
            if recorde is None or tempo_final < recorde:
                salvar_recorde(tempo_final)
                recorde = tempo_final

        # UI
        if venceu:
            texto = fonte.render('Vitória! Tempo: %.2fs' % tempo_final, True, CORES['texto'])
            tela.blit(texto, (LARGURA_TELA//2 - texto.get_width()//2, 10))
        else:
            tempo_atual = time.time() - tempo_inicio
            texto = fonte.render('Tempo: %.2fs' % tempo_atual, True, CORES['texto'])
            tela.blit(texto, (10, 10))
        if recorde:
            texto_rec = fonte.render('Recorde: %.2fs' % recorde, True, CORES['texto'])
            tela.blit(texto_rec, (10, 50))
        texto_reiniciar = fonte.render('Pressione R para reiniciar', True, CORES['texto'])
        tela.blit(texto_reiniciar, (10, ALTURA_TELA-40))

        pygame.display.flip()
        relogio.tick(30)

    pygame.quit()

if __name__ == '__main__':
    main() 