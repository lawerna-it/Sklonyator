from flask import Flask, request, jsonify, Response, json
import pymorphy2

app = Flask(__name__)

# Initialize the MorphAnalyzer
morph = pymorphy2.MorphAnalyzer()


def inflect_word(word, grammatical_case, number='sing'):
    """
    Inflects a word to the specified grammatical case.

    :param word: The word to inflect.
    :param grammatical_case: The grammatical case to inflect the word into (e.g., 'gent' for genitive).
    :return: The inflected word or None if the inflection is not possible.
    """
    parsed_word = morph.parse(word)[0]

    # Detect if the word is in plural form
    if parsed_word.tag.number == 'plur' and number == 'plur':
        inflected_word = parsed_word.inflect({grammatical_case})
    elif parsed_word.tag.number == 'plur' and number == 'sing':
        inflected_word = parsed_word.inflect({grammatical_case, 'sing'})
    else:
        inflected_word = parsed_word.inflect({grammatical_case, number})

    if inflected_word:
        return inflected_word.word
    return None

def get_plural(word):
    parsed_word = morph.parse(word)[0]
    inflected_word = parsed_word.inflect({'plur', 'nomn'})

    if not inflected_word:
        for case in ['gent', 'datv', 'accs', 'ablt', 'loct']:
            inflected_word = parsed_word.inflect({'plur', case})
            if inflected_word:
                break

    if inflected_word:
        return inflected_word.word
    return None

def jsonify_utf8(data):
    return Response(json.dumps(data, ensure_ascii=False), content_type='application/json; charset=utf-8')

@app.route('/inflect', methods=['GET'])
def inflect_get():
    word = request.args.get('word')
    grammatical_case = request.args.get('case')
    number = request.args.get('number', 'sing')

    if not word or not grammatical_case:
        return jsonify({'error': 'Both "word" and "case" must be provided.'}), 400

    inflected_word = inflect_word(word, grammatical_case, number)

    if inflected_word:
        return jsonify_utf8(inflected_word)
    else:
        return jsonify({'error': f'Could not inflect word "{word}" to case "{grammatical_case}".'}), 400

@app.route('/plural', methods=['GET'])
def plural_get():
    word = request.args.get('word')

    if not word:
        return jsonify({'error': 'The "word" must be provided.'}), 400

    plural_word = get_plural(word)

    if plural_word:
        return jsonify_utf8(plural_word)
    else:
        return jsonify({'error': f'Could not get plural form for word "{word}".'}), 400


if __name__ == '__main__':
    app.run(debug=True)