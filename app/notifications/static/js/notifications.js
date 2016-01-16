var notifications_timer_delay = 30000;
var notifications_menu_button;
var notifications_dropdown_button;
var notifications_content_list;
var notifications_content_url;
var notifications_initial_content_url;
var notifications_container;
var notifications_vanilla_page_title;
var notifications_previous_page = null;
var notifications_fetch_failed = false;

var notifications_button_template = "/notifications/button.html";
var notifications_list_template = "/notifications/list.html";

function notifications_safe_title(title){
    return title.replace(/\((\d+)\)/g,'⟨$1⟩');
}

function notifications_init_display(container, menu_button, dropdown_button, content_list, get_url) {
    notifications_container = container;
    notifications_menu_button = menu_button;
    notifications_dropdown_button = dropdown_button;
    notifications_content_list = content_list;
    notifications_content_url = get_url;
    notifications_initial_content_url = get_url;
    notifications_vanilla_page_title = notifications_safe_title(document.title);


    if ($(notifications_content_list)) {
        setInterval(notifications_refresh, notifications_timer_delay);
        notifications_refresh();
    };
}

function notifications_refresh() {
    $.get(notifications_content_url, function(data) {
        notifications_previous_page = data.previous;
        $(notifications_dropdown_button).html(nunjucks.render(notifications_button_template, data));
        $(notifications_content_list).html(nunjucks.render(notifications_list_template, data));
        $(notifications_menu_button).html(nunjucks.render(notifications_button_template, data));
        var prefix_title;
        if (data.count == 0) {
            $(notifications_container).hide();
            prefix_title = '';
        } else {
            $(notifications_container).show();
            prefix_title = '(' + data.count + ') ';
        }
        if (notifications_vanilla_page_title) {
            document.title = prefix_title + notifications_vanilla_page_title;
        }
        notification_initialize();
    }).error(function(){
        if (notifications_previous_page){ // We can not fetch the notifications, let's try to load the last previously known page
            notifications_fetch_failed = true;
            notifications_content_url = notifications_previous_page;
            notifications_previous_page = null;
            notifications_refresh();
        } else if (notifications_fetch_failed) { // The last previous one failed, let's try the original url
            notifications_fetch_failed = false; // avoid infinite loop
            notifications_content_url = notifications_initial_content_url;
            notifications_refresh();
        } else { // We can really not load the notifications...
            $(notifications_container).show();
            $(notifications_dropdown_button).html(nunjucks.render(notifications_button_template, {'error': true}));
            $(notifications_content_list).html(nunjucks.render(notifications_list_template, {'error': true}));
            $(notifications_menu_button).html(nunjucks.render(notifications_button_template, {'error': true}));
            if (notifications_vanilla_page_title) {
                document.title = notifications_vanilla_page_title;
            }
        }
    });
}

function notification_initialize() {
    notifications_fetch_failed = false;
    $(".notification_list .notification_dismiss a.close").click(function (e) {
        e.stopPropagation(); // Prevent dropdown to close
    });
    $(".notification_pagination > div > a").click(function(e) {
        e.stopPropagation(); // Prevent dropdown to close
    });
}

function notification_dismiss(url, target) {
    // Disable click propagation (to keep dropdown opened)
    function done(data) {
        // Dismiss target
        notifications_refresh();
    }
    $("#"+target+" a.close").addClass("fa-spinner fa-spin");
    $.ajax({url: url, type: 'DELETE'}).done(done);
}

function notifications_change_page(url){
  notifications_content_url = url;
  notifications_refresh();
}
