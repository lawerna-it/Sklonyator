from flask import Flask, request, jsonify
import pymorphy2

app = Flask(__name__)

# Initialize the MorphAnalyzer
morph = pymorphy2.MorphAnalyzer()


def inflect_word(word, grammatical_case):
    """
    Inflects a word to the specified grammatical case.

    :param word: The word to inflect.
    :param grammatical_case: The grammatical case to inflect the word into (e.g., 'gent' for genitive).
    :return: The inflected word or None if the inflection is not possible.
    """
    parsed_word = morph.parse(word)[0]
    inflected_word = parsed_word.inflect({grammatical_case})

    if inflected_word:
        return inflected_word.word
    return None


@app.route('/inflect', methods=['POST'])
def inflect():
    data = request.get_json()
    word = data.get('word')
    grammatical_case = data.get('case')

    if not word or not grammatical_case:
        return jsonify({'error': 'Both "word" and "case" must be provided.'}), 400

    inflected_word = inflect_word(word, grammatical_case)

    if inflected_word:
        return jsonify(inflected_word)
    else:
        return jsonify({'error': f'Could not inflect word "{word}" to case "{grammatical_case}".'}), 400


if __name__ == '__main__':
    app.run(debug=True)