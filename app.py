# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from modsec_manager import list_rules, toggle_rule, save_rule

app = Flask(__name__)
app.secret_key = 'a3f0b8c42fa67a5de4e0b8f21d7b3a76'

@app.route('/')
def dashboard():
    enabled_rules, disabled_rules = list_rules()
    return render_template('dashboard.html', enabled_rules=enabled_rules, disabled_rules=disabled_rules)

@app.route('/toggle_rule/<filename>')
def toggle_rule_view(filename):
    enabled_rules, disabled_rules = list_rules()  # Unpack the two lists properly
    all_rules = enabled_rules + disabled_rules      # Combine them to search for the rule
    
    rule = next((rule for rule in all_rules if rule['filename'] == filename), None)
    if rule:
        toggle_rule(filename, not rule['enabled'])
        flash(f"Rule '{filename}' {'enabled' if not rule['enabled'] else 'disabled'} successful!")
    return redirect(url_for('dashboard'))

@app.route('/edit_rule/<filename>', methods=['GET', 'POST'])
def edit_rule(filename):
    rule = next((rule for rule in list_rules() if rule['filename'] == filename), None)
    if not rule:
        flash("Rule not found.")
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        content = request.form['content']
        save_rule(filename, content)
        flash(f"Rule '{filename}' updated successfully.")
        return redirect(url_for('dashboard'))
    
    return render_template('rule_editor.html', rule=rule)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
