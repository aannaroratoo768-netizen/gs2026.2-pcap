class Orientacao:
    def __init__(self, id_orientacao, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em):
        self.id = id_orientacao
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    def exibir(self, pontos=None, confianca=None):
        print("\n" + "=" * 60)
        if pontos is not None and confianca is not None:
            print(f"Confiança da resposta: {confianca} ({pontos} pontos)")
        print(f">> {self.titulo} [{self.categoria}]")
        print(f"\n{self.resposta}\n")
        
        print("Documentos necessários:")
        if self.documentos:
            for doc in self.documentos:
                print(f"  - {doc}")
        else:
            print("  - Nenhum documento específico exigido.")
            
        print(f"\nOnde ir / acessar: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("Aviso: este assistente NÃO é um canal oficial.")
        print("=" * 60)
