from api.urbandb import UrbanDB

UrbanDB.open_pygres("./sessions/database-env.json")
UrbanDB.initialize_database()

def menu():
    print("1. ADD PRODUCT")
    print("2. DISPLAY ALL PRODUCTS")
    print("3. GET PRODUCT BY ID")
    print("Q. QUIT")
    return input("CHOOSE AN OPTION: ")

while (choice := menu()).upper() != 'Q':
    if choice == '1':
        UrbanDB.create_product({
            "id": (id := input("Enter product ID: ")),
            "name": input("Enter product name: "),
            "description": input("Enter description: ")
        })
        while input("Create variation? (Y/N) ").upper() == 'Y':
            UrbanDB.create_variation({
                "extension": input("Enter variation extension: "),
                "subname": input("Enter subname: "),
                "price": int(input("Enter price: ")),
                "display": True,
                "listing_id": id
            })
    elif choice == '2':
        for listing in UrbanDB.get_product_list():
            print(listing)
    elif choice == '3':
        print(UrbanDB.get_product(input("Enter the product ID: ")))
    else:
        print("ERROR")

UrbanDB.close_pygres()