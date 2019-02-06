
(function () {

    // Status bar

    function showURL(ev) {

        var msg = document.createElement("span");
        if (this.pathname == window.location.pathname &&
            this.protocol == window.location.protocol &&
            this.host     == window.location.host) {
            msg.innerHTML = this.hash;
        } else if (this.protocol == "mailto:") {
            msg.innerHTML = this.hostname + this.pathname;
        } else {
            msg.innerHTML = this.protocol + "//" + this.hostname
                + "<span class=\"href-path\">"
                + this.port + this.pathname + this.search + this.hash
                + "</span>";
        }

        var sbar = document.createElement("div");
        sbar.id = "status-bar";
        sbar.appendChild(msg);

        document.body.insertBefore(sbar, document.body.lastChild);
    }

    function hideURL(ev) {
        var sbar = document.getElementById("status-bar");
        if (sbar) {
            sbar.parentNode.removeChild(sbar);
        }
    }

    // Generated TOC

    function generateTOC() {

        var toc = document.getElementById("generated-toc");

        if (toc) {
            toc.parentNode.removeChild(toc);
        }

        toc = document.createElement("div");
        toc.id = "generated-toc";
        toc.style.display = "none";
        document.body.insertBefore(toc, document.body.lastChild);

        var headings = [].slice.call(document.body.querySelectorAll("h1, h2, h3, h4, h5, h6"));

        headings.forEach(function (heading, i) {

            var ref = "";

            if (heading.id) {
                ref = heading.getAttribute("id");
            } else {
                ref = "toc-" + i;
                heading.id = ref;
            }

            var link = document.createElement("a");
            link.href = "#" + ref;
            link.textContent = heading.innerText || heading.textContent;
            // link.appendChild(document.createTextNode(heading.innerText));

            if (i == 0) {
                link.id = "generated-toc-first-link";
            }

            var entry = document.createElement("div");
            entry.className = "toc-" + heading.tagName.toLowerCase();
            entry.appendChild(link);
            toc.appendChild(entry);

        });

        var hidetoc = document.createElement("a");
        hidetoc.id = "generated-toc-hide-toc";
        hidetoc.textContent = "Hide";
        hidetoc.title = "Hide Navigation pane";
        hidetoc.addEventListener ("click", function() { toc.style.display = "none" });
        toc.appendChild(hidetoc);

    }

    // Startup

    generateTOC();

    var links = [].slice.call(document.links);
    links.forEach(function (link) {
        link.addEventListener("mouseover", showURL);
        link.addEventListener("mouseout",  hideURL);
    });

    var items = [].slice.call(document.body.querySelectorAll('li'));
    items.forEach(function (item) {
        if (item.firstChild.nodeName == "INPUT" &&
            item.firstChild.getAttribute("type") == "checkbox") {
            item.classList.add("task-list-item");
        }
    });

})()

function toggleTOC() {
    var toc = document.getElementById("generated-toc");
    if (toc) {
        if (toc.style.display == "none") {
            toc.style.display = "block";
            document.getElementById("generated-toc-first-link").focus();
        } else {
            toc.style.display = "none";
            document.body.focus();
        }
    }
}

