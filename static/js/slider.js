$(function(){
  const slider = $('input[type=range]');
  slider.on('mouseenter',function(){
    let value = slider.val();
    slider.on('click',function(){
      value = slider.val();
      updateBackground(value);
    });
    slider.on('mousemove',function(){
      value = slider.val();
      updateBackground(value);
    });
  });
  function updateBackground(step){
      let n = step;
      slider.css({
        'background-image':'-webkit-linear-gradient(left ,#df5032 0%,#df5032 '+n+'%,#fff '+n+'%, #fff 100%)'
      });
  }
});