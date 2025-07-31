const linkUpload = document.querySelector("#linkUpload");
const fileUpload = document.querySelector("#fileUpload");
const linkfileUpload = document.querySelector("#linkfileUpload");
const crawlerSelector = document.querySelector('#crawlerSelector');

function handleCrawlerSelector () {
    const option = crawlerSelector.value
    if(option == "link"){
        linkUpload.style.display = "grid";
        fileUpload.style.display = "none";
        linkfileUpload.style.display = "none";
    }
    else if(option == "file"){
        linkUpload.style.display = "none";
        fileUpload.style.display = "block";
        linkfileUpload.style.display = "none";
    }
    else if(option == "linkfile"){
        linkUpload.style.display = "none";
        fileUpload.style.display = "none";
        linkfileUpload.style.display = "block";
    }
}

function handleLoader(element) {
    element.innerHTML = "Fetching";
}