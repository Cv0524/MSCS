from flask import Flask, render_template, request
import hashlib

app = Flask(__name__)

class BloomFilter:
    def __init__(self, size=32, hash_count=3):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [0] * size
        self.added_elements = []

    def _hash(self, item, seed):
        hash_string = f"{seed}_{item}".encode('utf-8')
        hex_hash = hashlib.md5(hash_string).hexdigest()
        return int(hex_hash, 16) % self.size

    def get_indices(self, item):
        return [self._hash(item, i) for i in range(self.hash_count)]

    def add(self, item):
        if item and item not in self.added_elements:
            self.added_elements.append(item)
            
        indices = self.get_indices(item)
        for i in indices:
            self.bit_array[i] = 1
        return indices

    def check(self, item):
        indices = self.get_indices(item)
        for i in indices:
            if self.bit_array[i] == 0:
                return False, indices
        return True, indices

    def reset(self):
        self.bit_array = [0] * self.size
        self.added_elements = []

bloom_filter = BloomFilter()

@app.route('/', methods=['GET', 'POST'])
def index():
    # Variables to pass to the Jinja template
    check_result = None
    checked_item = ""
    highlight_indices = []

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            item = request.form.get('add_item', '').strip()
            if item:
                bloom_filter.add(item)
                
        elif action == 'check':
            item = request.form.get('check_item', '').strip()
            if item:
                is_in, indices = bloom_filter.check(item)
                highlight_indices = indices
                checked_item = item
                if is_in:
                    check_result = "possibly_in"
                else:
                    check_result = "definitely_not"
                    
        elif action == 'reset':
            bloom_filter.reset()

    # Pass all state variables to Jinja
    return render_template(
        'index.html',
        bit_array=bloom_filter.bit_array,
        added_elements=bloom_filter.added_elements,
        check_result=check_result,
        checked_item=checked_item,
        highlight_indices=highlight_indices
    )
if __name__ == '__main__':
    app.run(debug=True)