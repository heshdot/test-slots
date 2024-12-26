from flask import Flask, jsonify, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

STARTING_BALANCE = 1000
MAX_LINES = 3
ROWS = 3
COLS = 3

symbol_count = {
    "A": 2,
    "B": 4,
    "C": 6,
    "D": 8
}

symbol_value = {
    "A": 5,
    "B": 4,
    "C": 3,
    "D": 2
}

def get_slot_machine_spin(rows, cols, symbols):
    all_symbols = []
    for symbol, symbol_count in symbols.items():
        for _ in range(symbol_count):
            all_symbols.append(symbol)

    columns = []
    for _ in range(cols):
        column = []
        current_symbols = all_symbols[:]
        for _ in range(rows):
            value = random.choice(current_symbols)
            current_symbols.remove(value)
            column.append(value)

        columns.append(column)

    return columns

@app.route('/')
def home():
    if 'wallet' not in session:
        session['wallet'] = STARTING_BALANCE
    return render_template('index.html', wallet=session['wallet'])

@app.route('/spin', methods=['POST'])
def spin():
    data = request.get_json()
    lines = data['lines']
    bet = data['bet']
    
    if bet * lines > session['wallet']:
        return jsonify({'error': 'Insufficient funds'})
    
    session['wallet'] -= bet * lines
    slots = get_slot_machine_spin(ROWS, COLS, symbol_count)
    winnings, winning_lines = check_winnings(slots, lines, bet, symbol_value)
    session['wallet'] += winnings
    
    result = {
        'slots': slots,
        'winnings': winnings,
        'winning_lines': winning_lines,
        'wallet': session['wallet']
    }
    return jsonify(result)

@app.route('/quit', methods=['POST'])
def quit_game():
    final_balance = session.get('wallet', STARTING_BALANCE)
    session.clear()
    return jsonify({
        'message': 'Thanks for playing!',
        'final_balance': final_balance
    })

def check_winnings(columns, lines, bet, values):
    winnings = 0
    winning_lines = []
    for line in range(lines):
        symbol = columns[0][line]
        for column in columns:
            symbol_to_check = column[line]
            if symbol != symbol_to_check:
                break
        else:
            winnings += values[symbol] * bet
            winning_lines.append(line + 1)

    return winnings, winning_lines

if __name__ == '__main__':
    app.run(debug=True)
