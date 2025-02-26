def calculator():
    """Kalkulator dengan lebih banyak fitur."""
    
    while True:
        print("\nSilakan pilih operasi:")
        print("1. Tambah")
        print("2. Kurang")
        print("3. Kali")
        print("4. Bagi")
        print("5. Keluar")

        choice = input("Masukkan pilihan Anda (1/2/3/4/5): ")

        if choice in ('1', '2', '3', '4'):
            try:
                num1 = float(input("Masukkan angka pertama: "))
                num2 = float(input("Masukkan angka kedua: "))
            except ValueError:
                print("Input tidak valid. Masukkan angka.")
                continue

            if choice == '1':
                result = num1 + num2
                print(f"{num1} + {num2} = {round(result, 3)}")

            elif choice == '2':
                result = num1 - num2
                print(f"{num1} - {num2} = {round(result, 3)}")

            elif choice == '3':
                result = num1 * num2
                print(f"{num1} × {num2} = {round(result, 3)}")

            elif choice == '4':
                if num2 == 0:
                    print("Error: Pembagian dengan nol!")
                else:
                    result = num1 / num2
                    print(f"{num1} ÷ {num2} = {round(result, 3)}")

        elif choice == '5':
            print("Keluar dari kalkulator.")
            break
        else:
            print("Pilihan tidak valid.")

# Memanggil fungsi kalkulator
calculator()
