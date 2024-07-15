from dice.dice import expression, recorder

def main():
    string = "5d6L2"
    tre = expression.parse_string(
        string, parse_all=True 
    )
    result = [x.evaluate() for x in tre][0]
    print('\n'.join(recorder))
    print(result)


if __name__ == "__main__":
    main()
