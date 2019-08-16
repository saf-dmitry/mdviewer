
MathJax.Hub.Config({
    jax: ["input/TeX", "output/HTML-CSS"],
    extensions: ["tex2jax.js", "MathMenu.js"],
    tex2jax: {
        inlineMath: [["$","$"], ["\\(","\\)"]],
        displayMath: [["$$","$$"], ["\\[","\\]"]],
        processRefs: true,
        processEscapes: true,
        processEnvironments: true
    },
    TeX: {
        equationNumbers: {
            autoNumber: "AMS"
        },
        extensions: ["AMSmath.js",
                     "AMSsymbols.js",
                     "noErrors.js",
                     "noUndefined.js"]
        Macros: {
            "ohm": "\\unicode{x2126}",
            "micro": "\\unicode{x00b5}",
            "degree": "\\unicode{x00b0}"
        },
    },
    "HTML-CSS": {
        scale: 98,
        fonts: ["Latin-Modern", "TeX", "STIX-Web"]
    }
});

MathJax.Ajax.loadComplete("[MathJax]/config/local/mathjax_config.js");

