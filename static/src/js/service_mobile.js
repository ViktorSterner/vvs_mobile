odoo.define('service_mobile.index', function (require) {
    'use strict';  

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');

    //~ Odoos översättningsfunktion
    var _t = core._t;

    console.log("working");

    //~ Kontrollera att klass finns på sidan (inte ladda i onödan)
    if (!$('.service_mobile').length) { 
        return $.Deferred().reject("DOM doesn't contain '.service_mobile'");
    }

    $('.prio_toggle').on('click', function (ev) {
        ev.preventDefault();

        console.log(ev);
        console.log("clicked");
    });

    $('.send_invoice').on('click', function (ev) {
        //~ If this method is called, the default action of the event will not be triggered.
        ev.preventDefault();

        var $link = $(ev.currentTarget);
        
        //~ Logga länken användaren klickade på 
        console.log($link.data('href'));
        
        // href pekar unikt på respektive order, använder inloggning från sessionen när vi anropar vår controller /service/<model("sale.order"):order>/order/flag
        // ajax.jsonRpc($link.data('href'), 'call', {})  
        //     .then(function (data) {
                
        //         //~ Logga responsen från vår controller
        //         console.log(data);
                
        //         // Felhantering
        //         if(data.error) {
        //             var $warning;
        //             if(data.error === 'anonymous_user') {
        //                 $warning = $('<div class="alert alert-danger alert-dismissable oe_forum_alert" id="flag_alert">'+
        //                     '<button type="button" class="close notification_close" data-dismiss="alert" aria-hidden="true">&times;</button>'+
        //                     _t('Sorry you must be logged in to flag a post') +
        //                     '</div>');
        //             } else if(data.error === 'post_non_flaggable') {
        //                 $warning = $('<div class="alert alert-danger alert-dismissable oe_forum_alert" id="flag_alert">'+
        //                     '<button type="button" class="close notification_close" data-dismiss="alert" aria-hidden="true">&times;</button>'+
        //                     _t('This post can not be flagged') +
        //                     '</div>');
        //             }
                    
        //             //~ Hitta meddelanderutan för länken 
        //             var flag_alert = $link.parent().find("#flag_alert");
                    
        //             //~ Lägg in varningen i vår meddelanderuta
        //             if (flag_alert.length === 0) {
        //                 $link.parent().append($warning);
        //             }
                    
        //         } else if(data.success) {
        //             //~ Om allt går bra: logga lite data:
        //             console.log(data.success);
        //             console.log(data.flag_value);
                    
        //             //~ Uppdatera vår textruta med prio. 
        //             if(data.flag_value === true) {
        //                 // Sätt texten i div med id="order_status_???" till Prio eller Normal beroende på om prio är true/false
        //                 $("#prio_status_" + data.order_id).html("Prio");
        //             } else {
        //                 $("#prio_status_" + data.order_id).html("Normal");
        //             }
        //         }
        //     });
    });

    // Hitta på sidan
    $('.flag').on('click', function (ev) {
        
        //~ If this method is called, the default action of the event will not be triggered.
        ev.preventDefault();
        
        var $link = $(ev.currentTarget);
        
        //~ Logga länken användaren klickade på 
        console.log($link.data('href'));
        
        // href pekar unikt på respektive order, använder inloggning från sessionen när vi anropar vår controller /service/<model("sale.order"):order>/order/flag
        ajax.jsonRpc($link.data('href'), 'call', {})  
            .then(function (data) {
                
                //~ Logga responsen från vår controller
                console.log(data);
                
                // Felhantering
                if(data.error) {
                    var $warning;
                    if(data.error === 'anonymous_user') {
                        $warning = $('<div class="alert alert-danger alert-dismissable oe_forum_alert" id="flag_alert">'+
                            '<button type="button" class="close notification_close" data-dismiss="alert" aria-hidden="true">&times;</button>'+
                            _t('Sorry you must be logged in to flag a post') +
                            '</div>');
                    } else if(data.error === 'post_non_flaggable') {
                        $warning = $('<div class="alert alert-danger alert-dismissable oe_forum_alert" id="flag_alert">'+
                            '<button type="button" class="close notification_close" data-dismiss="alert" aria-hidden="true">&times;</button>'+
                            _t('This post can not be flagged') +
                            '</div>');
                    }
                    
                    //~ Hitta meddelanderutan för länken 
                    var flag_alert = $link.parent().find("#flag_alert");
                    
                    //~ Lägg in varningen i vår meddelanderuta
                    if (flag_alert.length === 0) {
                        $link.parent().append($warning);
                    }
                    
                } else if(data.success) {
                    //~ Om allt går bra: logga lite data:
                    console.log(data.success);
                    console.log(data.flag_value);
                    
                    //~ Uppdatera vår textruta med prio. 
                    if(data.flag_value === true) {
                        // Sätt texten i div med id="order_status_???" till Prio eller Normal beroende på om prio är true/false
                        $("#prio_status_" + data.order_id).html("Prio");
                    } else {
                        $("#prio_status_" + data.order_id).html("Normal");
                    }
                }
            });
    });
});
