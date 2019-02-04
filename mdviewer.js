
(function () {

    function showURL (ev) {

        var msg = document.createElement("span");
        if (this.pathname == window.location.pathname &&
            this.protocol == window.location.protocol &&
            this.host     == window.location.host) {
            msg.innerHTML = "Go to <strong>" + this.hash + "</strong>";
        } else if (this.protocol == "mailto:") {
            msg.innerHTML = "Send email to <strong>" + this.hostname + this.pathname + "</strong>";
        } else {
            msg.innerHTML = "Open " + this.protocol + "//"
                + "<strong>" + this.hostname + "</strong>"
                + this.port + this.pathname + this.search + this.hash;
        }

        var sbar = document.createElement("div");
        sbar.id = "status-bar";
        sbar.appendChild(msg);

        document.body.insertBefore(sbar, document.body.lastChild);
    }

    function hideURL (ev) {
        var sbar = document.getElementById("status-bar");
        if (sbar) {
            sbar.parentNode.removeChild(sbar);
        }
    }

    var links = document.links;
    for(var i = 0; i < links.length; i++){
        var link = links[i];
        link.addEventListener('mouseover', showURL);
        link.addEventListener('mouseout',  hideURL);
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

        var ref = "";

        if (heading.id) {
            ref = heading.getAttribute("id");
        } else {
            ref = "toc-" + i;
            heading.id = ref;
        }

        var link = documentRef.createElement("a");
        link.href = "#" + ref;
        link.textContent = heading.innerText || heading.textContent;
        // link.appendChild(document.createTextNode(heading.innerText));

        var entry = documentRef.createElement("div");
        entry.className = "toc-" + heading.tagName.toLowerCase();
        entry.appendChild(link);
        toc.appendChild(entry);

        if (i === 0) {
            link.focus();
        }

    });

    var hidetoc = documentRef.createElement("a");

    hidetoc.id = "hide-toc";
    hidetoc.textContent = "Hide";
    hidetoc.title = "Hide Navigation pane";

    hidetoc.addEventListener ("click", function() {
        toc.parentNode.removeChild(toc);
    });

    toc.appendChild(hidetoc);

}

