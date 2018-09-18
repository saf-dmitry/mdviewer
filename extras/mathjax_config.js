
MathJax.Hub.Config({
    showProcessingMessages: false,
    messageStyle: "none",
    jax: ["input/TeX",
          "output/HTML-CSS"],
    extensions: ["tex2jax.js",
                 "MathMenu.js",
                 "MathZoom.js"],
    tex2jax: {
        inlineMath: [ ["$","$"], ["\\(","\\)"] ],
        displayMath: [ ["$$","$$"], ["\\[","\\]"] ],
        processRefs: true,
        processEscapes: true,
        processEnvironments: true
    },
    TeX: {
        equationNumbers: {
            autoNumber: "all"
        },
        extensions: ["AMSmath.js",
                     "AMSsymbols.js",
                     "noErrors.js",
                     "noUndefined.js"],
        Macros: {
            "micro": "\\unicode{xb5}",
            "ohm": "\\unicode{x2126}"
        },
    },
    "HTML-CSS": {
        preferredFont: "TeX",
        imageFont: null,
        linebreaks: {
            automatic: false
        },
        noReflows: true,
        EqnChunk: 10,
        EqnChunkFactor: 1,
        EqnChunkDelay: 10
    }
});

MathJax.Ajax.loadComplete("[MathJax]/config/local/mathjax_config.js");

