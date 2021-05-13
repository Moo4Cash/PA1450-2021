function collapse(item) {
    item.classList.toggle("expanded");
    var content = item.nextElementSibling;
    if (content.style.maxHeight){
        content.style.maxHeight = null;
      } else {
        content.style.maxHeight = content.scrollHeight + "px";
    }
}