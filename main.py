import livrosV2

usuario_logado_admin = True

def menu_principal():
    while True:
        print("\n========== ORBITLIT ==========")
        print("1 - Login e Cadastro")
        print("2 - Acervo de livros")
        print("3 - A decdir")
        print("0 - Sair")

        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            login.menu()
        elif opcao == "2":
            livrosV2.iniciar(usuario_logado_admin)
        elif opcao == "3":
            grupos.menu()
        elif opcao == "0":
            print("Encerrando o sistema.")
            break
        else:
            print("Opcao invalida. Tente novamente.")


if __name__ == "__main__":
    menu_principal()