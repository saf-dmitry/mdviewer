
(function () {

    function showURL (ev) {
        var href = this.href;
        var sbar = document.createElement("div");
        sbar.id = "status-bar";
        sbar.appendChild(document.createTextNode(href));
        document.body.insertBefore(sbar, document.body.lastChild);
    }

    function hideURL (ev) {
        var sbar = document.getElementById("status-bar");
        if (sbar) {
            sbar.parentNode.removeChild(sbar);
        }
    }

    var links = document.links;
    for(var i=0; i < links.length; i++){
        var a = links[i];
        a.addEventListener('mouseover', showURL);
        a.addEventListener('mouseout',  hideURL);
    }

})()

function generateTOC(documentRef) {

    var documentRef = documentRef || document;
    var headings = [].slice.call(documentRef.body.querySelectorAll("h1, h2, h3, h4, h5, h6"));

    var toc = documentRef.getElementById("generated-toc");

    if (toc) {
        toc.parentNode.removeChild(toc);
    }

    toc = document.createElement("div");
    toc.id = "generated-toc";
    document.body.insertBefore(toc, document.body.lastChild);

    headings.forEach(function (heading, i) {

        var ref = "toc-" + i;

        if (heading.id)
            ref = heading.getAttribute("id");
        else
            heading.id = ref;

        var link = documentRef.createElement("a");
        link.href = "#" + ref;
        link.textContent = heading.textContent;

        var div = documentRef.createElement("div");
        div.className = "toc-" + heading.tagName.toLowerCase();
        div.appendChild(link);
        toc.appendChild(div);

        if (i === 0) {
            link.focus();
        }

    });

    var hidetoc = documentRef.createElement("a");

    hidetoc.id = "hide-toc";
    hidetoc.textContent = "Hide";

    hidetoc.addEventListener ("click", function() {
        toc.parentNode.removeChild(toc);
    });

    toc.appendChild(hidetoc);

}

