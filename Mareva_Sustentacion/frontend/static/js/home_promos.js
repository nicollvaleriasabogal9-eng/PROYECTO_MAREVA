document.addEventListener("DOMContentLoaded",()=>{
    const slides=[...document.querySelectorAll(".promo-slide")];
    const dots=document.getElementById("promoDots");
    const prev=document.getElementById("promoPrev");
    const next=document.getElementById("promoNext");
    if(!slides.length)return;
    let index=0,timer;
    slides.forEach((_,i)=>{
        const button=document.createElement("button");
        button.type="button";
        button.className="promo-dot";
        button.setAttribute("aria-label",`Ver promoción ${i+1}`);
        button.onclick=()=>{
            show(i);
            restart();
        };
        dots.appendChild(button);
    });
    function show(i){
        index=(i+slides.length)%slides.length;
        slides.forEach((slide,n)=>slide.classList.toggle("is-active",n===index));
        [...dots.children].forEach((dot,n)=>dot.classList.toggle("is-active",n===index));
    }
    function restart(){
        clearInterval(timer);
        timer=setInterval(()=>show(index+1),5000);
    }
    prev?.addEventListener("click",()=>{
        show(index-1);
        restart();
    });
    next?.addEventListener("click",()=>{
        show(index+1);
        restart();
    });
    show(0);
    restart();
});