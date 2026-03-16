"""
Script para gerar commits com datas aleatorias entre junho/2025 e hoje.
Usa GIT_AUTHOR_DATE e GIT_COMMITTER_DATE para definir a data de cada commit
sem precisar alterar o relogio do sistema.

Uso:
  1. Crie um repositorio git (git init) ou aponte para um existente.
  2. Execute: python generate_commits.py
"""

import os
import random
import subprocess
import sys
from datetime import datetime, timedelta

# ─── CONFIGURACAO ────────────────────────────────────────────────────────────

REPO_DIR = os.path.dirname(os.path.abspath(__file__))  # pasta deste script
START_DATE = datetime(2025, 6, 1)                       # inicio: 01/jun/2025
END_DATE = datetime.now()                                # fim: hoje

# Faixa de commits por dia (dias que serao escolhidos)
MIN_COMMITS_PER_DAY = 1
MAX_COMMITS_PER_DAY = 6

# Probabilidade de um dia ter commits (0.0 a 1.0)
# ~40% dos dias terao commits, simulando atividade real
DAY_ACTIVITY_PROBABILITY = 0.40

# Mensagens de commit possiveis
COMMIT_MESSAGES = [
    # fixes
    "fix: corrigir erro de validacao no formulario",
    "fix: resolver problema de conexao com banco de dados",
    "fix: ajustar calculo de impostos",
    "fix: corrigir bug no envio de email",
    "fix: resolver conflito de dependencias",
    "fix: corrigir erro 500 na rota de autenticacao",
    "fix: ajustar formatacao de datas",
    "fix: resolver memory leak no processamento de arquivos",
    # features
    "feat: adicionar endpoint de exportacao CSV",
    "feat: implementar autenticacao via OAuth2",
    "feat: criar modulo de notificacoes push",
    "feat: adicionar suporte a paginacao na API",
    "feat: implementar cache com Redis",
    "feat: criar dashboard de metricas",
    "feat: adicionar filtro avancado de busca",
    "feat: implementar upload de arquivos em lote",
    # releases
    "release: v1.0.0 - lancamento inicial",
    "release: v1.1.0 - melhorias de performance",
    "release: v1.2.0 - novos relatorios",
    "release: v1.3.0 - integracao com servicos externos",
    "release: v2.0.0 - redesign completo da API",
    # chores / outros
    "chore: atualizar dependencias do projeto",
    "chore: configurar CI/CD pipeline",
    "chore: adicionar linting e formatacao automatica",
    "docs: atualizar README com instrucoes de deploy",
    "docs: documentar endpoints da API",
    "refactor: reorganizar estrutura de pastas",
    "refactor: simplificar logica de autorizacao",
    "test: adicionar testes unitarios para modulo de pagamentos",
    "test: cobrir cenarios de erro na API",
    "perf: otimizar queries do relatorio mensal",
    "style: padronizar nomes de variaveis",
]

# Nome do arquivo que sera modificado para gerar os commits
COMMIT_FILE = "history.log"

# ─── FUNCOES ─────────────────────────────────────────────────────────────────


def run_git(*args, env_extra=None):
    """Executa um comando git no REPO_DIR."""
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(
        ["git"] + list(args),
        cwd=REPO_DIR,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  ERRO git {' '.join(args)}: {result.stderr.strip()}")
    return result


def ensure_repo():
    """Garante que o diretorio e um repositorio git com pelo menos 1 commit."""
    git_dir = os.path.join(REPO_DIR, ".git")
    if not os.path.isdir(git_dir):
        print(f"Inicializando repositorio em {REPO_DIR} ...")
        run_git("init")
        # Criar commit inicial
        filepath = os.path.join(REPO_DIR, COMMIT_FILE)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Historico de commits\n")
        run_git("add", COMMIT_FILE)
        run_git("commit", "-m", "chore: commit inicial")
        print("Repositorio inicializado com commit inicial.\n")
    else:
        print(f"Repositorio encontrado em {REPO_DIR}\n")


def generate_commit_plan():
    """
    Gera um plano: lista de (datetime, mensagem) ordenada cronologicamente.
    """
    total_days = (END_DATE - START_DATE).days
    if total_days <= 0:
        print("ERRO: START_DATE deve ser anterior a END_DATE.")
        sys.exit(1)

    plan = []
    for day_offset in range(total_days + 1):
        current_date = START_DATE + timedelta(days=day_offset)

        # Decidir se esse dia tera commits
        if random.random() > DAY_ACTIVITY_PROBABILITY:
            continue

        # Quantos commits nesse dia
        num_commits = random.randint(MIN_COMMITS_PER_DAY, MAX_COMMITS_PER_DAY)

        for _ in range(num_commits):
            # Hora aleatoria entre 08:00 e 22:00
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            commit_dt = current_date.replace(hour=hour, minute=minute, second=second)
            message = random.choice(COMMIT_MESSAGES)
            plan.append((commit_dt, message))

    # Ordenar por data
    plan.sort(key=lambda x: x[0])
    return plan


def execute_plan(plan):
    """Executa cada commit do plano usando GIT_AUTHOR_DATE/GIT_COMMITTER_DATE."""
    filepath = os.path.join(REPO_DIR, COMMIT_FILE)
    total = len(plan)

    for i, (commit_dt, message) in enumerate(plan, 1):
        # Formato ISO 8601 para o git
        date_str = commit_dt.strftime("%Y-%m-%dT%H:%M:%S")

        # Adicionar uma linha ao arquivo para gerar mudanca
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"[{date_str}] {message}\n")

        # Stage + commit com data customizada
        run_git("add", COMMIT_FILE)

        env_dates = {
            "GIT_AUTHOR_DATE": date_str,
            "GIT_COMMITTER_DATE": date_str,
        }
        run_git("commit", "-m", message, env_extra=env_dates)

        # Progresso
        if i % 20 == 0 or i == total:
            print(f"  [{i}/{total}] commits criados...")

    print()


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  GERADOR DE COMMITS ALEATORIOS")
    print("=" * 60)
    print(f"  Periodo: {START_DATE.strftime('%d/%m/%Y')} ate {END_DATE.strftime('%d/%m/%Y')}")
    print(f"  Repositorio: {REPO_DIR}")
    print(f"  Probabilidade de atividade/dia: {DAY_ACTIVITY_PROBABILITY * 100:.0f}%")
    print(f"  Commits por dia ativo: {MIN_COMMITS_PER_DAY}-{MAX_COMMITS_PER_DAY}")
    print()

    ensure_repo()

    print("Gerando plano de commits...")
    plan = generate_commit_plan()
    print(f"  Total de commits a criar: {len(plan)}")
    print(f"  Primeiro: {plan[0][0].strftime('%d/%m/%Y %H:%M')}" if plan else "")
    print(f"  Ultimo:   {plan[-1][0].strftime('%d/%m/%Y %H:%M')}" if plan else "")
    print()

    confirm = input("Deseja prosseguir? (s/n): ").strip().lower()
    if confirm != "s":
        print("Cancelado.")
        sys.exit(0)

    print("\nCriando commits...\n")
    execute_plan(plan)

    # Resumo
    result = run_git("log", "--oneline")
    total_commits = len(result.stdout.strip().splitlines())
    print(f"Pronto! Repositorio agora tem {total_commits} commits no total.")
    print(f"Use 'git log --oneline' para verificar.")
    print(f"Use 'git log --graph --all --oneline' para visualizar.")


if __name__ == "__main__":
    main()
