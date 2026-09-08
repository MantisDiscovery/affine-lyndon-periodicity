(function () {
  'use strict';

  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // keep selectors and node creation small enough to read beside the mathematics
  function $(selector, root) {
    return (root || document).querySelector(selector);
  }

  function $$(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function sameWord(a, b) {
    return a.length === b.length && a.every(function (letter, index) { return letter === b[index]; });
  }

  function wordText(word) {
    return word.join('');
  }

  // these factors come from code/classical/classical_words.py
  var EXAMPLES = {
    C3: {
      label: 'C₃⁽¹⁾ · order 1<3<0<2',
      rows: [
        { left: [1, 2, 3], period: [1, 2, 3, 1, 2, 0], right: [1, 2, 0], parent: 1 },
        { left: [1, 2, 1, 2, 0], period: [1, 2, 3, 1, 2, 0], right: [3], parent: 1 },
        { left: [1, 0, 1, 2, 3], period: [1, 2, 0, 1, 2, 3], right: [2], parent: 1 }
      ]
    },
    D4: {
      label: 'D₄⁽¹⁾ · order 2<0<1<3<4',
      rows: [
        { left: [2, 3, 1, 0], period: [2, 3, 1, 0, 2, 4], right: [2, 4], parent: 1 },
        { left: [2, 3, 1, 2, 4], period: [2, 3, 1, 0, 2, 4], right: [0], parent: 1 },
        { left: [2, 3, 0, 2, 4], period: [2, 3, 1, 0, 2, 4], right: [1], parent: 1 },
        { left: [2, 1, 0, 2, 4], period: [2, 3, 1, 0, 2, 4], right: [3], parent: 1 }
      ]
    }
  };

  function appendLetters(host, word, extraClass) {
    word.forEach(function (value) {
      var letter = document.createElement('span');
      letter.className = 'letter' + (extraClass ? ' ' + extraClass : '');
      letter.textContent = value;
      host.appendChild(letter);
    });
  }

  function initWordExplorer() {
    var exampleSelect = $('#word-example');
    var indexSelect = $('#word-index');
    var degree = $('#word-degree');
    var stage = $('#word-stage');
    if (!exampleSelect || !indexSelect || !degree || !stage) return;
    var timer = null;

    function stop() {
      if (timer) window.clearInterval(timer);
      timer = null;
      $('#play-degree').textContent = 'Play degrees';
    }

    function fillIndices() {
      clear(indexSelect);
      EXAMPLES[exampleSelect.value].rows.forEach(function (_, index) {
        var option = document.createElement('option');
        option.value = index;
        option.textContent = 'i = ' + (index + 1);
        indexSelect.appendChild(option);
      });
      if (exampleSelect.value === 'C3') indexSelect.value = '2';
    }

    function makeGroup(kind, letters, copy) {
      var group = document.createElement('span');
      group.className = 'factor-group factor-' + kind;
      if (copy) group.setAttribute('data-copy', copy);
      appendLetters(group, letters);
      return group;
    }

    function render() {
      var example = EXAMPLES[exampleSelect.value];
      var row = example.rows[Number(indexSelect.value)];
      var k = Number(degree.value);
      clear(stage);

      var line = document.createElement('div');
      line.className = 'word-line';
      line.appendChild(makeGroup('left', row.left));
      for (var copy = 1; copy < k; copy += 1) line.appendChild(makeGroup('period', row.period, String(copy)));
      line.appendChild(makeGroup('right', row.right));
      stage.appendChild(line);

      var summary = document.createElement('p');
      summary.className = 'word-summary';
      summary.textContent = example.label + ', i = ' + (Number(indexSelect.value) + 1) + ', k = ' + k + ', length ' + (k * row.period.length) + '.';
      stage.appendChild(summary);

      $('#word-degree-value').textContent = 'k = ' + k;
      $('#factor-left').textContent = wordText(row.left);
      $('#factor-period').textContent = wordText(row.period);
      $('#factor-right').textContent = wordText(row.right);
      $('#factor-parent').textContent = 'i = ' + row.parent;
    }

    exampleSelect.addEventListener('change', function () { stop(); fillIndices(); render(); });
    indexSelect.addEventListener('change', function () { stop(); render(); });
    degree.addEventListener('input', function () { stop(); render(); });
    $('#play-degree').addEventListener('click', function () {
      if (reducedMotion) {
        degree.value = Number(degree.value) === 6 ? 1 : Number(degree.value) + 1;
        render();
        return;
      }
      if (timer) { stop(); return; }
      this.textContent = 'Pause';
      timer = window.setInterval(function () {
        degree.value = Number(degree.value) === 6 ? 1 : Number(degree.value) + 1;
        render();
      }, 900);
    });

    fillIndices();
    render();
  }

  // construct the two palindromic arms from the type-c proof
  function arms(n, r) {
    var left = [];
    var right = [];
    for (var a = r - 1; a >= 0; a -= 1) left.push(a);
    for (var a2 = 1; a2 < r; a2 += 1) left.push(a2);
    for (var b = r + 1; b <= n; b += 1) right.push(b);
    for (var b2 = n - 1; b2 > r; b2 -= 1) right.push(b2);
    return { left: left, right: right };
  }

  function alphabetOrder(n, r, direction) {
    var others = [];
    for (var letter = 0; letter <= n; letter += 1) if (letter !== r) others.push(letter);
    if (direction === 'descending') others.reverse();
    return [r].concat(others);
  }

  // merge arm prefixes by taking the greater available letter
  function greatestShuffle(left, right, order) {
    var rank = new Map();
    order.forEach(function (letter, index) { rank.set(letter, index); });
    var a = left.slice();
    var b = right.slice();
    var word = [];
    while (a.length || b.length) {
      if (!b.length || (a.length && rank.get(a[0]) > rank.get(b[0]))) word.push(a.shift());
      else word.push(b.shift());
    }
    return word;
  }

  function signedCoordinate(sign, index) {
    return (sign > 0 ? '+' : '−') + 'e' + index;
  }

  function finiteWeight(n, r, p, q) {
    var s = n - r;
    var x = p < r ? signedCoordinate(1, r - p) : signedCoordinate(-1, p - r + 1);
    var z = q < s ? signedCoordinate(-1, r + 1 + q) : signedCoordinate(1, 2 * n - r - q);
    return x + ' ' + z;
  }

  function initBlockGrid() {
    var rankSelect = $('#grid-rank');
    var cutSelect = $('#grid-cut');
    var orderSelect = $('#grid-order');
    var host = $('#block-grid');
    if (!rankSelect || !cutSelect || !host) return;
    var selected = { p: 0, q: 0 };

    function fillCuts() {
      var n = Number(rankSelect.value);
      var prior = Number(cutSelect.value) || 1;
      clear(cutSelect);
      for (var r = 1; r < n; r += 1) {
        var option = document.createElement('option');
        option.value = r;
        option.textContent = r;
        cutSelect.appendChild(option);
      }
      cutSelect.value = String(Math.min(prior, n - 1));
    }

    function render() {
      var n = Number(rankSelect.value);
      var r = Number(cutSelect.value);
      var s = n - r;
      var H = 2 * r - 1;
      var J = 2 * s - 1;
      var complement = { p: H - selected.p, q: J - selected.q };
      var arm = arms(n, r);
      var order = alphabetOrder(n, r, orderSelect.value);

      selected.p = Math.min(selected.p, H);
      selected.q = Math.min(selected.q, J);
      complement = { p: H - selected.p, q: J - selected.q };
      clear(host);
      host.style.gridTemplateColumns = 'repeat(' + (J + 1) + ', minmax(34px, 1fr))';

      for (var p = 0; p <= H; p += 1) {
        for (var q = 0; q <= J; q += 1) {
          var cell = document.createElement('button');
          cell.type = 'button';
          cell.className = 'grid-cell';
          if (p === selected.p && q === selected.q) cell.classList.add('selected');
          else if (p === complement.p && q === complement.q) cell.classList.add('complement');
          cell.textContent = p + ',' + q;
          cell.setAttribute('aria-label', 'block degree d ' + p + ' ' + q);
          (function (nextP, nextQ) {
            cell.addEventListener('click', function () {
              selected = { p: nextP, q: nextQ };
              render();
            });
          })(p, q);
          host.appendChild(cell);
        }
      }

      var shuffle = greatestShuffle(arm.left.slice(0, selected.p), arm.right.slice(0, selected.q), order);
      var blockWord = [r].concat(shuffle);
      $('#grid-cell').textContent = 'd(' + selected.p + ',' + selected.q + ')';
      $('#grid-weight').textContent = finiteWeight(n, r, selected.p, selected.q);
      $('#grid-complement').textContent = 'd(' + complement.p + ',' + complement.q + ')';
      $('#grid-word').textContent = wordText(blockWord);
      host.setAttribute('aria-label', 'Type C block grid with ' + (4 * r * s) + ' roots, ' + (H + 1) + ' rows and ' + (J + 1) + ' columns');
    }

    rankSelect.addEventListener('change', function () { fillCuts(); selected = { p: 0, q: 0 }; render(); });
    cutSelect.addEventListener('change', function () { selected = { p: 0, q: 0 }; render(); });
    orderSelect.addEventListener('change', render);
    fillCuts();
    cutSelect.value = '2';
    render();
  }

  function renderPhaseWord(host, first, second, firstClass, secondClass) {
    clear(host);
    appendLetters(host, first, firstClass);
    appendLetters(host, second, secondClass);
  }

  function initPhase() {
    var control = $('#phase-cut');
    if (!control) return;
    var parent = [1, 2, 3, 1, 2, 0];
    var period = [1, 2, 0, 1, 2, 3];
    var left = [1, 0, 1, 2, 3];

    function render() {
      var length = Number(control.value);
      var split = parent.length - length;
      var A = parent.slice(0, split);
      var C = parent.slice(split);
      var rotation = C.concat(A);
      var matches = sameWord(rotation, period);
      $('#phase-cut-value').textContent = length;
      renderPhaseWord($('#phase-parent'), A, C, 'a', 'c');
      renderPhaseWord($('#phase-rotation'), C, A, 'c', 'a');
      renderPhaseWord($('#phase-target'), period, [], 'a', '');
      renderPhaseWord($('#phase-preperiod'), left, C, 'l', 'c');
      var verdict = $('#phase-verdict');
      verdict.classList.toggle('match', matches);
      verdict.textContent = matches
        ? 'This is the unique selected cut: the rotation equals W, so y = L C = ' + wordText(left.concat(C)) + '.'
        : 'This cyclic cut gives ' + wordText(rotation) + ', which is not the selected period W = ' + wordText(period) + '.';
    }

    control.addEventListener('input', render);
    render();
  }

  function initChrome() {
    var bar = $('.topbar');
    var progress = $('.progress');
    var links = $$('.topbar nav a');
    var targets = links.map(function (link) { return $(link.getAttribute('href')); });

    function setViewportWidth() {
      document.documentElement.style.setProperty('--vw', document.documentElement.clientWidth + 'px');
    }

    function onScroll() {
      var y = window.scrollY;
      bar.classList.toggle('stuck', y > 8);
      var available = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.width = (available > 0 ? Math.min(100, 100 * y / available) : 0) + '%';
      var active = 0;
      targets.forEach(function (target, index) {
        if (target && target.getBoundingClientRect().top < 140) active = index;
      });
      links.forEach(function (link, index) { link.classList.toggle('on', index === active); });
    }

    var toggle = $('.themetoggle');
    var stored = null;
    try { stored = window.localStorage.getItem('affine-lyndon-theme'); } catch (error) { stored = null; }
    if (stored) document.documentElement.setAttribute('data-theme', stored);
    toggle.setAttribute('aria-pressed', String(document.documentElement.getAttribute('data-theme') === 'dark'));
    toggle.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-theme');
      if (!current) current = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      var next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      toggle.setAttribute('aria-pressed', String(next === 'dark'));
      try { window.localStorage.setItem('affine-lyndon-theme', next); } catch (error) { /* storage can be unavailable */ }
    });

    if ('IntersectionObserver' in window && !reducedMotion) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('in');
            observer.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -40px 0px' });
      $$('.reveal').forEach(function (node) { observer.observe(node); });
    } else {
      $$('.reveal').forEach(function (node) { node.classList.add('in'); });
    }

    $('#copybib').addEventListener('click', function () {
      var button = this;
      window.navigator.clipboard.writeText($('#bibtex').textContent).then(function () {
        button.textContent = 'Copied';
        window.setTimeout(function () { button.textContent = 'Copy BibTeX'; }, 1400);
      });
    });

    setViewportWidth();
    window.addEventListener('resize', setViewportWidth);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  function boot() {
    initChrome();
    initWordExplorer();
    initBlockGrid();
    initPhase();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
