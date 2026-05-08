/* Quiz generator — single-page app, vanilla JS */
(() => {
  'use strict';

  const QUIZ_DATA = JSON.parse(document.getElementById('quiz-data').textContent);
  const STORAGE_KEY = 'quiz-state-v1';

  const EXERCISE_COUNT = 10;
  const QUESTIONS_PER_EXERCISE = 30;          // nominal
  const EXERCISE_DURATION_MS = 60 * 60 * 1000; // 60 min
  const EXAM_QUESTIONS = 60;
  const EXAM_DURATION_MS = 90 * 60 * 1000;     // 90 min

  // ----- Storage -----
  const persisted = {
    exercises: null, // array of session descriptors (or null = not generated)
    examHistory: [], // last few exam runs
    exerciseResults: {}, // { [sessionIdx]: result }
  };

  function loadPersisted() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) Object.assign(persisted, JSON.parse(raw));
    } catch {}
  }
  function savePersisted() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(persisted));
    } catch {}
  }

  // ----- Helpers -----
  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function buildSessionFromIds(ids) {
    return ids.map((qid) => {
      const q = QUIZ_DATA.find((x) => x.id === qid);
      // answers: index 0 is correct in source PDF
      const indexed = q.answers.map((text, i) => ({ text, isCorrect: i === 0 }));
      const shuffled = shuffle(indexed);
      return {
        questionId: q.id,
        question: q.question,
        answers: shuffled.map((a) => a.text),
        correctIndex: shuffled.findIndex((a) => a.isCorrect),
      };
    });
  }

  function generateExercises() {
    const allIds = QUIZ_DATA.map((q) => q.id);
    const shuffledIds = shuffle(allIds);
    const sessions = [];
    // 10 sessions; 297 questions distributed as 9*30 + 1*27 (last one has fewer)
    let idx = 0;
    for (let s = 0; s < EXERCISE_COUNT; s++) {
      const remaining = shuffledIds.length - idx;
      const remainingSessions = EXERCISE_COUNT - s;
      const size = Math.min(QUESTIONS_PER_EXERCISE, Math.ceil(remaining / remainingSessions));
      const ids = shuffledIds.slice(idx, idx + size);
      idx += size;
      sessions.push({
        index: s,
        type: 'exercise',
        questions: buildSessionFromIds(ids),
      });
    }
    return sessions;
  }

  function generateExam() {
    const allIds = QUIZ_DATA.map((q) => q.id);
    const ids = shuffle(allIds).slice(0, EXAM_QUESTIONS);
    return {
      type: 'exam',
      questions: buildSessionFromIds(ids),
      generatedAt: Date.now(),
    };
  }

  function fmtTime(ms) {
    const negative = ms < 0;
    const tot = Math.abs(Math.floor(ms / 1000));
    const m = Math.floor(tot / 60);
    const s = tot % 60;
    return `${negative ? '-' : ''}${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }

  // ----- Runtime state (current session) -----
  let active = null;
  let timerHandle = null;
  let toastTimeout = null;

  function startSession(session, opts) {
    active = {
      session,
      type: session.type,
      durationMs: opts.durationMs,
      hardStop: opts.hardStop, // exam = true
      startedAt: Date.now(),
      finishedAt: null,
      answers: new Array(session.questions.length).fill(null),
      currentIdx: 0,
      timeUpFired: false,
    };
    render();
  }

  function tick() {
    if (!active || active.finishedAt) return;
    const elapsed = Date.now() - active.startedAt;
    const remaining = active.durationMs - elapsed;

    const timerEl = document.getElementById('timer');
    if (timerEl) {
      timerEl.textContent = fmtTime(remaining);
      timerEl.classList.toggle('over', remaining < 0);
      timerEl.classList.toggle('urgent', remaining > 0 && remaining < 5 * 60 * 1000);
    }

    if (remaining <= 0 && !active.timeUpFired) {
      active.timeUpFired = true;
      if (active.hardStop) {
        finishSession();
      } else {
        showToast('Tempo scaduto. Continua pure — verrà mostrato lo sforamento nel riepilogo.');
      }
    }
  }

  function showToast(msg, ms = 5000) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();
    if (toastTimeout) clearTimeout(toastTimeout);
    const t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    document.body.appendChild(t);
    toastTimeout = setTimeout(() => t.remove(), ms);
  }

  function finishSession() {
    if (!active) return;
    active.finishedAt = Date.now();
    if (timerHandle) { clearInterval(timerHandle); timerHandle = null; }

    const elapsed = active.finishedAt - active.startedAt;
    const remaining = active.durationMs - elapsed;
    const total = active.session.questions.length;
    let correct = 0, wrong = 0, blank = 0;
    active.session.questions.forEach((q, i) => {
      const a = active.answers[i];
      if (a === null || a === undefined) blank++;
      else if (a === q.correctIndex) correct++;
      else wrong++;
    });

    const result = {
      type: active.type,
      total,
      correct,
      wrong,
      blank,
      elapsedMs: elapsed,
      remainingMs: remaining, // negative = over time
      finishedAt: active.finishedAt,
      questions: active.session.questions,
      answers: active.answers,
      sessionIndex: active.session.index,
    };

    if (active.type === 'exercise') {
      persisted.exerciseResults[active.session.index] = result;
    } else {
      persisted.examHistory = [result, ...(persisted.examHistory || [])].slice(0, 10);
    }
    savePersisted();

    state.view = 'recap';
    state.recap = result;
    active = null;
    render();
  }

  // ----- View state -----
  const state = {
    view: 'home', // 'home' | 'session' | 'recap' | 'reviewExercise'
    recap: null,
    confirmModal: null,
  };

  function setView(view, data = {}) {
    Object.assign(state, { view, ...data });
    render();
  }

  // ----- Renderers -----
  const root = document.getElementById('app');

  function el(tag, props = {}, children = []) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(props)) {
      if (k === 'class') e.className = v;
      else if (k === 'on') {
        for (const [evt, fn] of Object.entries(v)) e.addEventListener(evt, fn);
      } else if (k === 'html') e.innerHTML = v;
      else if (k === 'style') Object.assign(e.style, v);
      else e.setAttribute(k, v);
    }
    for (const child of [].concat(children)) {
      if (child == null || child === false) continue;
      e.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
    }
    return e;
  }

  function render() {
    root.innerHTML = '';
    root.appendChild(renderHeader());

    let content;
    if (state.view === 'home') content = renderHome();
    else if (state.view === 'session') content = renderSession();
    else if (state.view === 'recap') content = renderRecap();
    else if (state.view === 'reviewExercise') content = renderRecap();

    root.appendChild(content);
    root.appendChild(renderFooter());
    if (state.confirmModal) root.appendChild(renderModal(state.confirmModal));
  }

  function renderHeader() {
    return el('header', { class: 'app-header' }, [
      el('h1', {}, 'Quiz Addetti UPP'),
      el('div', { class: 'meta' }, `${QUIZ_DATA.length} domande in banca dati`),
    ]);
  }

  function renderFooter() {
    return el('footer', { class: 'app-footer' }, [
      'Banca dati locale — i progressi sono salvati nel browser. ',
      el('a', {
        href: '#',
        class: 'back-link',
        on: { click: (e) => { e.preventDefault(); confirmReset(); } },
      }, 'Resetta tutti i dati'),
    ]);
  }

  function confirmReset() {
    state.confirmModal = {
      title: 'Resettare tutti i dati?',
      body: 'Verranno cancellate tutte le esercitazioni generate e i risultati. Operazione irreversibile.',
      confirmLabel: 'Resetta',
      confirmClass: 'btn danger',
      onConfirm: () => {
        persisted.exercises = null;
        persisted.examHistory = [];
        persisted.exerciseResults = {};
        savePersisted();
        state.confirmModal = null;
        setView('home');
      },
    };
    render();
  }

  function renderModal(m) {
    return el('div', {
      class: 'modal-backdrop',
      on: { click: (e) => { if (e.target.classList.contains('modal-backdrop')) { state.confirmModal = null; render(); } } },
    }, [
      el('div', { class: 'modal' }, [
        el('h3', {}, m.title),
        el('p', {}, m.body),
        el('div', { class: 'modal-actions' }, [
          el('button', {
            class: 'btn ghost',
            on: { click: () => { state.confirmModal = null; render(); } },
          }, 'Annulla'),
          el('button', {
            class: m.confirmClass || 'btn',
            on: { click: () => { m.onConfirm(); } },
          }, m.confirmLabel || 'Conferma'),
        ]),
      ]),
    ]);
  }

  function renderHome() {
    const wrap = el('div');

    wrap.appendChild(el('div', { class: 'actions-grid' }, [
      el('div', { class: 'card' }, [
        el('h2', {}, 'Esercitazioni'),
        el('p', {}, '10 sessioni che coprono tutte le domande senza ripetizioni. Ordine domande e risposte casuale. Timer 60 minuti per sessione (non blocca, mostra eventuale sforamento).'),
        el('div', { class: 'btn-row' }, [
          persisted.exercises
            ? el('button', { class: 'btn', on: { click: () => setView('home') } }, 'Continua')
            : null,
          el('button', {
            class: 'btn ' + (persisted.exercises ? 'secondary' : ''),
            on: { click: () => {
              if (persisted.exercises) {
                state.confirmModal = {
                  title: 'Rigenerare le esercitazioni?',
                  body: 'I risultati delle 10 sessioni esistenti verranno cancellati.',
                  confirmLabel: 'Rigenera',
                  onConfirm: () => {
                    persisted.exercises = generateExercises();
                    persisted.exerciseResults = {};
                    savePersisted();
                    state.confirmModal = null;
                    setView('home');
                  },
                };
                render();
              } else {
                persisted.exercises = generateExercises();
                savePersisted();
                setView('home');
              }
            } },
          }, persisted.exercises ? 'Rigenera Esercitazioni' : 'Genera Esercitazioni'),
        ]),
      ]),
      el('div', { class: 'card' }, [
        el('h2', {}, 'Esame'),
        el('p', {}, '60 domande casuali, risposte mescolate. Timer 90 minuti — alla scadenza la sessione si chiude automaticamente.'),
        el('div', { class: 'btn-row' }, [
          el('button', {
            class: 'btn success',
            on: { click: () => {
              const ex = generateExam();
              startSession(ex, { durationMs: EXAM_DURATION_MS, hardStop: true });
              setView('session');
              if (timerHandle) clearInterval(timerHandle);
              timerHandle = setInterval(tick, 250);
            } },
          }, 'Genera Esame'),
        ]),
      ]),
    ]));

    if (persisted.exercises) {
      const list = el('div', { class: 'session-list' });
      persisted.exercises.forEach((s, i) => {
        const result = persisted.exerciseResults[i];
        list.appendChild(renderSessionCard(s, i, result));
      });
      wrap.appendChild(el('div', {}, [
        el('h2', { style: { fontSize: '17px', marginTop: '8px' } }, 'Le tue 10 sessioni'),
        list,
      ]));
    }

    if (persisted.examHistory && persisted.examHistory.length) {
      const items = persisted.examHistory.slice(0, 5).map((r, i) => {
        const date = new Date(r.finishedAt).toLocaleString('it-IT');
        const pct = Math.round((r.correct / r.total) * 100);
        return el('div', { class: 'session-card' }, [
          el('div', { class: 'label' }, 'Esame'),
          el('div', { class: 'title' }, date),
          el('div', { class: 'score' }, `${r.correct}/${r.total} (${pct}%)`),
          el('button', {
            class: 'btn ghost',
            on: { click: () => setView('recap', { recap: r }) },
          }, 'Rivedi'),
        ]);
      });
      wrap.appendChild(el('div', { style: { marginTop: '24px' } }, [
        el('h2', { style: { fontSize: '17px' } }, 'Ultimi esami'),
        el('div', { class: 'session-list' }, items),
      ]));
    }

    return wrap;
  }

  function renderSessionCard(s, i, result) {
    const card = el('div', { class: 'session-card' + (result ? ' completed' : '') });
    card.appendChild(el('div', { class: 'label' }, `Sessione ${i + 1}`));
    card.appendChild(el('div', { class: 'title' }, `${s.questions.length} domande`));
    if (result) {
      const pct = Math.round((result.correct / result.total) * 100);
      card.appendChild(el('div', { class: 'score' }, `${result.correct}/${result.total} (${pct}%)`));
      const btnRow = el('div', { class: 'btn-row' }, [
        el('button', {
          class: 'btn ghost',
          on: { click: () => setView('recap', { recap: result }) },
        }, 'Rivedi'),
        el('button', {
          class: 'btn secondary',
          on: { click: () => {
            startSession(s, { durationMs: EXERCISE_DURATION_MS, hardStop: false });
            setView('session');
            if (timerHandle) clearInterval(timerHandle);
            timerHandle = setInterval(tick, 250);
          } },
        }, 'Rifai'),
      ]);
      card.appendChild(btnRow);
    } else {
      card.appendChild(el('div', { class: 'status' }, 'Non iniziata'));
      card.appendChild(el('button', {
        class: 'btn',
        on: { click: () => {
          startSession(s, { durationMs: EXERCISE_DURATION_MS, hardStop: false });
          setView('session');
          if (timerHandle) clearInterval(timerHandle);
          timerHandle = setInterval(tick, 250);
        } },
      }, 'Start'));
    }
    return card;
  }

  function renderSession() {
    if (!active) return el('div', {}, 'Nessuna sessione attiva.');
    const wrap = el('div');
    const elapsed = Date.now() - active.startedAt;
    const remaining = active.durationMs - elapsed;
    const answeredCount = active.answers.filter((a) => a !== null && a !== undefined).length;

    wrap.appendChild(el('div', { class: 'quiz-header' }, [
      el('div', { class: 'progress' }, [
        active.type === 'exam' ? 'Esame' : `Esercitazione ${active.session.index + 1}`,
        ` · ${answeredCount}/${active.session.questions.length} risposte`,
      ]),
      el('div', { id: 'timer', class: 'timer' }, fmtTime(remaining)),
      el('button', {
        class: 'btn danger',
        on: { click: () => {
          state.confirmModal = {
            title: 'Terminare la sessione?',
            body: 'Le risposte non date verranno conteggiate come saltate.',
            confirmLabel: 'Termina',
            confirmClass: 'btn danger',
            onConfirm: () => {
              state.confirmModal = null;
              finishSession();
            },
          };
          render();
        } },
      }, 'Termina'),
    ]));

    active.session.questions.forEach((q, qi) => {
      const block = el('div', { class: 'question-block', id: `q-${qi}` });
      block.appendChild(el('div', { class: 'q-num', style: { fontSize: '13px', color: 'var(--muted)', marginBottom: '8px' } }, `Domanda ${qi + 1}`));
      block.appendChild(el('div', { class: 'question-text' }, q.question));
      const list = el('div', { class: 'answer-list' });
      q.answers.forEach((aText, ai) => {
        const isSel = active.answers[qi] === ai;
        const item = el('div', {
          class: 'answer' + (isSel ? ' selected' : ''),
          on: { click: () => {
            active.answers[qi] = ai;
            render();
          } },
        }, [
          el('div', { class: 'marker' }, String.fromCharCode(65 + ai)),
          el('div', {}, aText),
        ]);
        list.appendChild(item);
      });
      block.appendChild(list);
      wrap.appendChild(block);
    });

    wrap.appendChild(el('div', { class: 'btn-row', style: { marginTop: '20px', justifyContent: 'flex-end' } }, [
      el('button', {
        class: 'btn',
        on: { click: () => finishSession() },
      }, 'Concludi e vedi risultati'),
    ]));

    return wrap;
  }

  function renderRecap() {
    const r = state.recap;
    if (!r) return el('div', {}, 'Nessun risultato.');
    const wrap = el('div');

    wrap.appendChild(el('a', {
      href: '#',
      class: 'back-link',
      on: { click: (e) => { e.preventDefault(); setView('home'); } },
    }, '← Torna alla home'));

    const pct = Math.round((r.correct / r.total) * 100);
    const overTime = r.remainingMs < 0;

    wrap.appendChild(el('h2', { style: { marginTop: '8px' } }, `Riepilogo ${r.type === 'exam' ? 'Esame' : `Esercitazione ${r.sessionIndex + 1}`}`));

    wrap.appendChild(el('div', { class: 'summary-grid' }, [
      el('div', { class: 'stat success' }, [
        el('div', { class: 'stat-label' }, 'Corrette'),
        el('div', { class: 'stat-value' }, `${r.correct} / ${r.total}`),
      ]),
      el('div', { class: 'stat danger' }, [
        el('div', { class: 'stat-label' }, 'Sbagliate'),
        el('div', { class: 'stat-value' }, String(r.wrong)),
      ]),
      el('div', { class: 'stat warning' }, [
        el('div', { class: 'stat-label' }, 'Saltate'),
        el('div', { class: 'stat-value' }, String(r.blank)),
      ]),
      el('div', { class: 'stat' }, [
        el('div', { class: 'stat-label' }, 'Punteggio'),
        el('div', { class: 'stat-value' }, `${pct}%`),
      ]),
      el('div', { class: 'stat' + (overTime ? ' danger' : ' success') }, [
        el('div', { class: 'stat-label' }, overTime ? 'Tempo sforato' : 'Tempo rimanente'),
        el('div', { class: 'stat-value' }, fmtTime(r.remainingMs)),
      ]),
      el('div', { class: 'stat' }, [
        el('div', { class: 'stat-label' }, 'Durata'),
        el('div', { class: 'stat-value' }, fmtTime(r.elapsedMs)),
      ]),
    ]));

    r.questions.forEach((q, qi) => {
      const userAns = r.answers[qi];
      const isCorrect = userAns === q.correctIndex;
      const isBlank = userAns === null || userAns === undefined;
      const block = el('div', { class: 'recap-question' });
      block.appendChild(el('div', { class: 'q-num' }, [
        `Domanda ${qi + 1}`,
        isBlank
          ? el('span', { class: 'tag your' }, 'Saltata')
          : isCorrect
            ? el('span', { class: 'tag correct' }, 'Corretta')
            : el('span', { class: 'tag wrong' }, 'Errata'),
      ]));
      block.appendChild(el('div', { class: 'q-text' }, q.question));
      q.answers.forEach((aText, ai) => {
        const isUser = ai === userAns;
        const isCorr = ai === q.correctIndex;
        const cls = ['recap-answer'];
        if (isCorr) cls.push('is-correct');
        if (isUser && !isCorr) cls.push('user-wrong');
        if (isUser && isCorr) cls.push('user-correct');
        const tags = [];
        if (isCorr) tags.push(el('span', { class: 'tag correct' }, 'Risposta corretta'));
        if (isUser) tags.push(el('span', { class: 'tag your' }, 'La tua risposta'));
        block.appendChild(el('div', { class: cls.join(' ') }, [
          el('div', {}, [
            el('strong', {}, String.fromCharCode(65 + ai) + '. '),
            aText,
            ...tags,
          ]),
        ]));
      });
      wrap.appendChild(block);
    });

    wrap.appendChild(el('div', { class: 'btn-row', style: { marginTop: '20px' } }, [
      el('button', { class: 'btn', on: { click: () => setView('home') } }, 'Torna alla home'),
    ]));

    return wrap;
  }

  // ----- Boot -----
  loadPersisted();
  render();
})();
