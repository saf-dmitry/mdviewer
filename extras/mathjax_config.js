
MathJax.Hub.Config({
    jax: ["input/TeX",
          "output/CommonHTML"],
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
                     "noUndefined.js",
                     "mhchem.js"],
        Macros: {
            "micro": "\\unicode{xb5}",
            "ohm": "\\unicode{x2126}"
        },
    },
    "CommonHTML": {
        linebreaks: {
            automatic: false
        }
    }
});

MathJax.Ajax.loadComplete("[MathJax]/config/local/mathjax_config.js");

