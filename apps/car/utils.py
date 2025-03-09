def format_price(predicted_price):
    """
    Formata o valor previsto no estilo monetário brasileiro.
    Converte para string e remove decimais.
    """
    formatted_prediction = str(int(predicted_price))

    if len(formatted_prediction) == 7:  # Caso o número tenha 7 dígitos (2 antes do ponto)
        formatted_prediction = formatted_prediction[:2] + "." + \
            formatted_prediction[2:5] + "," + formatted_prediction[5:]
    elif len(formatted_prediction) == 8:  # Caso o número tenha 8 dígitos (3 antes do ponto)
        formatted_prediction = formatted_prediction[:3] + "." + \
            formatted_prediction[3:6] + "," + formatted_prediction[6:]
    return formatted_prediction
