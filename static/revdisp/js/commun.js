
function afficheTooltip (monObjet) {
			
			
			
    if (document.documentElement.clientWidth >= 600) {
        
        
     initPositionTooltip (monObjet);

     if ($("#texte-" + monObjet).css("display") == "none") {
        $("#lien-" + monObjet).attr("aria-expanded", "true"); 
        
        $("#texte-" + monObjet).removeClass("cacher");
        $("#texte-" + monObjet).addClass("visible");
        
        $("#triangle-" + monObjet).removeClass("cacher");
        $("#triangle-" + monObjet).addClass("visible");

        $("#texte-" + monObjet).attr("aria-hidden", "false"); 	
        
        $("#texte-" + monObjet).focus();
    

     } else  {
         
        $("#triangle-" + monObjet).removeClass("visible");
        $("#triangle-" + monObjet).addClass("cacher");

        $("#texte-" + monObjet).removeClass("visible");
        $("#texte-" + monObjet).addClass("cacher");
         
        $("#texte-" + monObjet).attr("aria-hidden", "true"); 
        
                
        $("#lien-" + monObjet).focus();
        $("#lien-" + monObjet).attr("aria-expanded", "false"); 
        
        cacheFeuille (monObjet);
     
     }		 
    
    } else {
        
         //si la feuille est cacher alors affiche la feuille
        if ($("#feuille-" + monObjet).css("display") == "none") {
           
        
            afficheFeuille (monObjet);
         } else  {
             
            cacheFeuille (monObjet);
            cacheTooltip (monObjet);
         
        }
        
    }
        
    }
    
function cacheTooltip (monObjet) {
    
        $("#triangle-" + monObjet).removeClass("visible");
        $("#triangle-" + monObjet).addClass("cacher");

        
        $("#texte-" + monObjet).removeClass("visible");
        $("#texte-" + monObjet).addClass("cacher");
         
        $("#texte-" + monObjet).attr("aria-hidden", "true"); 
        
                
        $("#lien-" + monObjet).focus();
        $("#lien-" + monObjet).attr("aria-expanded", "false"); 


    }
    

function afficheTooltipMobile (monObjet) {
        
    
        
     
     if (document.documentElement.clientWidth < 600) {

        $("#texte-" + monObjet).removeClass("cacher");
        $("#texte-" + monObjet).addClass("visible");
        
            
        $("#texte-" + monObjet).attr("aria-hidden", "false"); 	
        
        $("#texte-" + monObjet).focus();



     } else  {
         $("#texte-" + monObjet).css({"position": "absolute"});
     
         
     
     // var posY = $(this).offset().top + $(this).height() - 2;  /* + 28; */ 

        
     if ($("#texte-" + monObjet).css("display") == "none") {
        $("#lien-" + monObjet).attr("aria-expanded", "true"); 
        
        
        $("#texte-" + monObjet).removeClass("cacher");
        $("#texte-" + monObjet).addClass("visible");
            
        $("#texte-" + monObjet).attr("aria-hidden", "false"); 	
        
        $("#x-" + monObjet).focus();
    

     } else  {
        $("#texte-" + monObjet).removeClass("visible");
        $("#texte-" + monObjet).addClass("cacher");
         
        $("#texte-" + monObjet).attr("aria-hidden", "true"); 
        
                
        $("#lien-" + monObjet).focus();
        $("#lien-" + monObjet).attr("aria-expanded", "false"); 
     
      }		 
     }
    
        
    }


function afficheFeuille (monObjet) {
        

        $("#lien-" + monObjet).attr("aria-expanded", "true"); 
        
        $("#feuille-" + monObjet).removeClass("cacher");
        $("#feuille-" + monObjet).addClass("visible");
            
        $("#feuille-" + monObjet).attr("aria-hidden", "false"); 	
        
        $("#feuille-" + monObjet).focus();
    
        
        
    }
    
    function cacheFeuille (monObjet) {
    
        
        $("#feuille-" + monObjet).removeClass("visible");
        $("#feuille-" + monObjet).addClass("cacher");
         
        $("#feuille-" + monObjet).attr("aria-hidden", "true"); 
        
                
        $("#lien-" + monObjet).focus();
        $("#lien-" + monObjet).attr("aria-expanded", "false"); 


    }
    
    
    
    
    function ouvrirBloc (monObjet, temps) {
    
     if ($("#bouton-" + monObjet).val() == "+") {
     
        $("#bouton-" + monObjet).val("−");
        $("#bouton-" + monObjet).attr("aria-expanded", "true"); 
        
        
        $( "#" + monObjet ).slideToggle("slow");

     } else  {
     
       $("#bouton-" + monObjet).val("+");
       $("#bouton-" + monObjet).attr("aria-expanded", "false"); 	
       
     
      $( "#" + monObjet ).slideToggle("slow");


     }
    }
    
    function ouvrirPlus (monObjet) {
    
     if ($("#bouton-" + monObjet).val() == "+") {
     
        $("#bouton-" + monObjet).val("–");
        $("#bouton-" + monObjet).attr("aria-expanded", "true"); 	
        $("." + monObjet).addClass("visible");
        $("." + monObjet).removeClass("cacher");
        

     } else  {
     
       $("#bouton-" + monObjet).val("+");
       $("#bouton-" + monObjet).attr("aria-expanded", "false"); 	
       $("." + monObjet).removeClass("visible");
       $("." + monObjet).addClass("cacher");
       
       $("." + monObjet + "-info").removeClass("visible");
       $("." + monObjet + "-info").addClass("cacher");

     }
    }
    
    
    
    function initPositionTooltip (monObjet) {
    
    
          var gaucheBouton = document.getElementById(monObjet).offsetLeft;

          var gaucheTooltip = document.getElementById("texte-" + monObjet).offsetLeft;
          
          var largeurTooltip = $("#texte-" + monObjet).width();
          
          
          if (((largeurTooltip / 2 )  + 50) > gaucheBouton) {
            document.getElementById("texte-" + monObjet).style.left = ( - (gaucheBouton - 10) ) + "px";


          } else if ((gaucheBouton + (largeurTooltip/2) + 40) >= document.documentElement.clientWidth) {
             if (largeurTooltip  > gaucheBouton) {
               document.getElementById("texte-" + monObjet).style.left = ( - (gaucheBouton - 10) ) + "px";

             } else   {
               document.getElementById("texte-" + monObjet).style.left = ( - (largeurTooltip - 40) )  + "px";
              
             }
          } else   {
            document.getElementById("texte-" + monObjet).style.left = ( - (largeurTooltip / 2 ) ) + "px";
            

          }
      
    }


  document.addEventListener('keydown', function(event){
       if ((event.key === "Escape") || (event.key === "Tab")){
       
            $(".triangle").removeClass("visible");
         $(".triangle").addClass("cacher");

         $(".tooltiptextBulle").removeClass("visible");
         $(".tooltiptextBulle").addClass("cacher"); 	
            
         $(".tooltiptextBulle").attr("aria-hidden", "true");
        
        
         $(".pointaide").attr("aria-expanded", "false"); 
       
            
       }
    });


   $(document).ready(function() {		

           $(".tooltiptextBulle").removeClass("visible");
        $(".tooltiptextBulle").addClass("cacher");
        
       //copie les textes dans les tooltip fixe pour le mobile

       var all_tooltip=document.getElementsByClassName("tooltipBulle");
       var idTooltip = ""
       var innerTooltip = ""
       for(var i=0;i<all_tooltip.length;i++)
       {
        idTooltip = all_tooltip[i].id;
        initPositionTooltip (idTooltip);
        if (document.getElementById("src-" + idTooltip) && document.getElementById("textfixe-" + idTooltip)) {
         innerTooltip = document.getElementById("src-" + idTooltip).innerHTML;
         document.getElementById("textfixe-" + idTooltip).innerHTML = innerTooltip;
        }
      }



      $(".tooltipBulle").hover(function() {
        var monId= $(this).attr("id");
       
           if (document.documentElement.clientWidth >= 600) {


          initPositionTooltip (monId);
          
          /* Cache tout les tooltip*/
          $(".triangle").removeClass("visible");
          $(".triangle").addClass("cacher");

          $(".tooltiptextBulle").removeClass("visible");
          $(".tooltiptextBulle").addClass("cacher"); 	
            
          $(".tooltiptextBulle").attr("aria-hidden", "true");
        
          $(".pointaide").attr("aria-expanded", "false"); 
         
           /* affiche le tooltip du bouton*/
          $("#lien-" + monId).attr("aria-expanded", "true"); 
        
          $("#texte-" + monId).removeClass("cacher");
          $("#texte-" + monId).addClass("visible");
          
          $("#triangle-" + monId).removeClass("cacher");
          $("#triangle-" + monId).addClass("visible");
            
          $("#texte-" + monId).attr("aria-hidden", "false"); 	
          
        
        }
       
      }, function() {
      
        var monId= $(this).attr("id");
        
        if (document.documentElement.clientWidth >= 600) {

         $("#triangle-" + monId).removeClass("visible");
         $("#triangle-" + monId).addClass("cacher");

         $("#texte-" + monId).removeClass("visible");
         $("#texte-" + monId).addClass("cacher");
            
         $("#texte-" + monId).attr("aria-hidden", "true"); 	
        
        
         $("#lien-" + monId).attr("aria-expanded", "false"); 
        }

     });		
         
        
    });
