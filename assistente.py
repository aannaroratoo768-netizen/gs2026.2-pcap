import csv
import json
import os
import time
from datetime import datetime


class Assistente:
    def __init__(self, nome, base, caminho_historico="data/historico.json", caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.historico = self._carregar_historico()
        self.nota_facilidade = None

    def _carregar_historico(self):
        if os.path.exists(self.caminho_historico):
            try:
                with open(self.caminho_historico, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    if isinstance(dados, list):
                        return dados
            except Exception:
                pass
        return []

    def _salvar_historico_json(self):
        os.makedirs(os.path.dirname(self.caminho_historico), exist_ok=True)
        with open(self.caminho_historico, "w", encoding="utf-8") as f:
            json.dump(self.historico, f, ensure_ascii=False, indent=2)

    def _contem_dados_pessoais(self, texto):
        if "@" in texto:
            return True
        digitos = sum(1 for c in texto if c.isdigit())
        if digitos >= 8:
            return True
        return False

    def _ler_sim_nao(self, mensagem):
        while True:
            resp = input(mensagem).strip().lower()
            if resp in ("s", "sim"):
                return True
            elif resp in ("n", "nao", "não"):
                return False
            print("Entrada inválida. Digite apenas 's' para sim ou 'n' para não.")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, tempo_segundos):
        registro = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo_segundos
        }
        self.historico.append(registro)
        self._salvar_historico_json()

    def perguntar(self):
        tentativas = 0
        inicio = time.time()

        while True:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if pergunta == "0":
                return

            if not pergunta:
                print("Entrada vazia. Por favor, digite sua dúvida ou 0 para voltar.")
                continue

            if self._contem_dados_pessoais(pergunta):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva sua dúvida sem dados pessoais.")
                continue

            tentativas += 1
            resultados = self.base.buscar(pergunta)

            # Melhor pontuação precisa ser >= 3
            if not resultados or resultados[0][0] < 3:
                tempo = round(time.time() - inicio, 1)
                print("\nNão encontrei uma orientação específica para essa dúvida.")
                print("Sugestão: tente usar palavras-chave mais diretas (ex: 'carteira de trabalho', 'cpf', 'titulo', 'fgts')")
                print(f"Ou navegue pelas categorias disponíveis: {', '.join(self.base.categorias())}")

                self.registrar(
                    origem="pergunta",
                    pergunta=pergunta,
                    id_orientacao=None,
                    encontrou=False,
                    ajudou=False,
                    tentativas=tentativas,
                    tempo_segundos=tempo
                )
                
                if not self._ler_sim_nao("\nDeseja reformular sua pergunta agora? (s/n): "):
                    return
                continue

            # Encontrou resultado válido (>= 3 pontos)
            melhor_pts, melhor_ori = resultados[0]
            confianca = "ALTA" if melhor_pts >= 6 else "MÉDIA"
            melhor_ori.exibir(pontos=melhor_pts, confianca=confianca)

            # Exibe até 2 alternativas (que também tenham >= 3 pontos)
            alternativas = [r for r in resultados[1:3] if r[0] >= 3]
            if alternativas:
                print("\nOutras orientações relacionadas:")
                for pts_alt, ori_alt in alternativas:
                    print(f"  * {ori_alt.titulo} [{ori_alt.categoria}] ({pts_alt} pts)")

            ajudou = self._ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            tempo = round(time.time() - inicio, 1)

            self.registrar(
                origem="pergunta",
                pergunta=pergunta,
                id_orientacao=melhor_ori.id,
                encontrou=True,
                ajudou=ajudou,
                tentativas=tentativas,
                tempo_segundos=tempo
            )

            if ajudou:
                print("Ótimo! Atendimento registrado.")
                return
            else:
                if not self._ler_sim_nao("Deseja tentar fazer outra pergunta? (s/n): "):
                    return
                inicio = time.time()

    def navegar(self):
        categorias = self.base.categorias()
        if not categorias:
            print("Nenhuma categoria disponível na base.")
            return

        while True:
            print("\n--- Categorias Disponíveis ---")
            for idx, cat in enumerate(categorias, start=1):
                print(f"{idx}. {cat}")
            print("0. Voltar")

            escolha = input("Escolha o número da categoria: ").strip()
            if escolha == "0":
                return

            if not escolha.isdigit() or not (1 <= int(escolha) <= len(categorias)):
                print("Opção inválida. Digite um número da lista.")
                continue

            cat_escolhida = categorias[int(escolha) - 1]
            orientacoes_cat = self.base.por_categoria(cat_escolhida)

            while True:
                print(f"\n--- Orientações em '{cat_escolhida}' ---")
                for idx, ori in enumerate(orientacoes_cat, start=1):
                    print(f"{idx}. {ori.titulo}")
                print("0. Voltar")

                escolha_ori = input("Escolha o número da orientação: ").strip()
                if escolha_ori == "0":
                    break

                if not escolha_ori.isdigit() or not (1 <= int(escolha_ori) <= len(orientacoes_cat)):
                    print("Opção inválida. Digite um número da lista.")
                    continue

                inicio = time.time()
                ori_selecionada = orientacoes_cat[int(escolha_ori) - 1]
                ori_selecionada.exibir()

                ajudou = self._ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
                tempo = round(time.time() - inicio, 1)

                self.registrar(
                    origem="categoria",
                    pergunta=f"Navegação: {ori_selecionada.titulo}",
                    id_orientacao=ori_selecionada.id,
                    encontrou=True,
                    ajudou=ajudou,
                    tentativas=1,
                    tempo_segundos=tempo
                )
                break

    def indicadores(self):
        total = len(self.historico)
        print("\n" + "=" * 50)
        print(f"INDICADORES DE ATENDIMENTO - {self.nome}")
        print("=" * 50)

        if total == 0:
            print("Nenhum atendimento registrado até o momento.")
            return

        encontrados = [h for h in self.historico if h["encontrou"]]
        ajudaram = [h for h in self.historico if h["ajudou"]]
        sem_solucao = [h["pergunta"] for h in self.historico if not h["encontrou"]]

        taxa_encontrada = (len(encontrados) / total) * 100
        taxa_acerto = (len(ajudaram) / total) * 100
        media_tentativas = sum(h["tentativas"] for h in self.historico) / total

        if encontrados:
            tempo_medio = sum(h["tempo_segundos"] for h in encontrados) / len(encontrados)
        else:
            tempo_medio = 0.0

        print(f"Total de atendimentos: {total}")
        print(f"Resposta encontrada (%): {taxa_encontrada:.1f}%")
        print(f"Tempo médio para encontrar: {tempo_medio:.1f}s")
        print(f"Taxa de acerto - ajudou (%): {taxa_acerto:.1f}%")
        print(f"Tentativas por atendimento: {media_tentativas:.1f}")
        
        if self.nota_facilidade is not None:
            print(f"Facilidade de uso (1 a 5): {self.nota_facilidade}")
        else:
            print("Facilidade de uso (1 a 5): Avaliada ao sair do sistema")

        print("\nLista de dúvidas sem solução:")
        if sem_solucao:
            for duvida in sem_solucao:
                print(f"  - {duvida}")
        else:
            print("  - Nenhuma dúvida ficou sem solução.")
        print("=" * 50)

    def exportar_csv(self):
        if not self.historico:
            print("Não há atendimentos registrados para exportar.")
            return

        os.makedirs(os.path.dirname(self.caminho_csv), exist_ok=True)
        campos = [
            "data", "origem", "pergunta", "id_orientacao",
            "encontrou", "ajudou", "tentativas", "tempo_segundos"
        ]

        try:
            with open(self.caminho_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(self.historico)
            print(f"Histórico exportado com sucesso para '{self.caminho_csv}'.")
        except Exception as e:
            print(f"[ERRO] Não foi possível exportar o CSV: {e}")

    def avaliar_facilidade(self):
        while True:
            nota = input("\nAntes de sair, avalie a facilidade de uso do assistente (1 a 5): ").strip()
            if nota.isdigit() and 1 <= int(nota) <= 5:
                self.nota_facilidade = int(nota)
                print(f"Obrigado! Nota {self.nota_facilidade} registrada.")
                break
            print("Entrada inválida. Digite um número inteiro de 1 a 5.")
