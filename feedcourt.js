function pagelinks(){
    var morelinks = document.getElementsByClassName('more')
    for (var i = 0 ; i < morelinks.length ; i++){
        console.log("making links");
        l = morelinks[i];
        l.addEventListener('click',function(){
            if (this.innerHTML == "more") {
                this.parentElement.parentElement.style.height = "auto";
                this.innerHTML = "less";
            }else {
                this.parentElement.parentElement.style.height = "30em";
                this.innerHTML = "more";
            }
        });
    }
}
