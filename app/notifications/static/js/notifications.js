var notifications_content_url;
var notifications_content;
var notifications_button_content_url;
var notifications_button_content;

function notifications_init_display(content, get_url) {
    notifications_content_url = get_url;
    notifications_content = content;
}

function notifications_button_init_display(content, get_url) {
    notifications_button_content_url = get_url;
    notifications_button_content = content;
}

function notifications_refresh() {
    $.get(notifications_content_url, function(data) {
        $(notifications_content).replaceWith(data);
    });
    $.get(notifications_button_content_url, function(data) {
        $(notifications_button_content).html(data);
    });
    notification_initialize();
}
