function TrieNode(){
    this.count = 0;
    this.next = {};
    this.exist = false;

    this.insert = function(word){
        let node = this;
        for (let i of word){
            // console.log(i, node.next)
            if (! (i in node.next)){
                node.next[i] = new TrieNode()
            }
            node = node.next[i];
            node.count ++;

        }
        node.exist = true;
    };

    this.search = function(word, prefix){
        let node = this;
        for (let i of word){
            node = node.next[i];
            if (!node){
                return false;
            }
        }
        if(node.exist || prefix){
            return node;
        }else{
            return false;
        }
    };

    this.get_through = function(root, out, is_root){
          let node = this;
          for (let i in node.next){
              let next_node = node.next[i];
              if (is_root){
                  next_node.word = i;
                  next_node.get_through(root, out)
              }else{
                  next_node.word = node.word.concat(i);
                  if (next_node.exist){
                      out[next_node.word] = next_node.count;
                  }
                  next_node.get_through(root, out)
              }
          }
          node.word = '';
    };

    this.with_prefix = function(prefix, include_prefix){
        let node = this.search(prefix, true);
        if (node === false){
            return node;
        }else{
            node.word = prefix;
            let out = {};
            if (include_prefix){
                out[prefix] = node.count;
            }
            node.get_through(node, out, false);
            return out
        }
    }
}

// var strings = ['But', 'it', 'also', 'shows', 'that', 'bilinguals', 'are', 'more', 'flexible', 'thinkers', 'append', 'already', 'it', 'iron', 'item'];

// var root = new TrieNode();

// for (let i of strings){
//     root.insert(i)
// }
// console.log('search "thinker": ', root.search('thinker'));
// console.log('search "thinkers": ', root.search('thinkers'));
// console.log(root.with_prefix('it', true));
// console.log(root.with_prefix('it', false));
// var out = {};
// root.get_through(root, out, true);
// console.log(out);
// console.log('a');

module.exports = TrieNode
