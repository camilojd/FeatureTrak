// call each of the properties of entityObj with the values of the same key at obj
function setModelValues(entityObj, obj) {
    for (var prop in entityObj) {
        if (entityObj.hasOwnProperty(prop)) {
            entityObj[prop](obj[prop])
        }
    }
}

function emptyObjectFromKnockoutModel(entityObj) {
    var ret = {};
    for (var prop in entityObj) {
        if (entityObj.hasOwnProperty(prop)) {
            var value = entityObj[prop]();
            var empty;
            if (typeof value == 'string' || typeof value == 'number') {
                empty = '';
            } else if (typeof value == 'boolean') {
                empty = false;
            } else {
                // assume list
                empty = [];
            }
            ret[prop] = empty;
        }
    }

    return ret;
}

var PagedGridModel = function(columns) {
    this.items = ko.observableArray([]);
    this.vm = new ko.simpleGrid.viewModel({
        data: this.items,
        columns: columns,
        pageSize: 5,
        editFn : function(id) {
            var entity = FT.admin.entity();
            
            container = FT.admin[entity];

            rest.GET('/api/v1/admin/' + entity + '/' + id, function(data) {
                setModelValues(container, data);
            }).then(function() {
                FT.admin.curEntityId = id;
                FT.admin.validationErrors([]);
                $('#frm' + entity).modal();
            });
        },
        deleteFn: function(id) {
            if (!confirm('Are you sure?')) {
                return;
            }

            var entity = FT.admin.entity();
            
            rest.DELETE('/api/v1/admin/' + entity + '/' + id)
            .then(function() {
                FT.admin.updateCurrentGrid();
            });
        }
    });
};

// idiomatic ajax helper
window.rest = {
    GET: function(url, callback) {
        return $.get(url, undefined, callback);
    },
    POST: function(url, data, callback) {
        data = JSON.stringify(data);
        return $.ajax(url, { data: data, type: 'POST', contentType: 'application/json', success: callback});
    },
    PUT: function(url, data, callback) {
        data = JSON.stringify(data);
        return $.ajax(url, { data: data, type: 'PUT', contentType: 'application/json', success: callback});
    },
    DELETE: function(url, callback) {
        return $.ajax(url, { type: 'DELETE', contentType: 'application/json', success: callback});
    }
}

var FT = {}
FT.curPage = ko.observable('login');

FT.showAlert = function(_alert) {
    var time = new Date().getTime();
    var type = _alert.type || 'info'; // also: danger, success, warning
    var html = '<div style="display:hidden" class="alert alert-' + type + ' alert-dismissible" data-aid="' + time + '" role="alert">' +
               '  <button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
               '    <span aria-hidden="true">&times;</span>' +
               '  </button>' +
               '  <strong>' + _alert.title + '</strong>' +
               '  <br>' + _alert.text +
               '</div>';

    $(html).hide().appendTo('#ft-growl-notifications').fadeIn(300);
    setTimeout(function() {
        var query = $('#ft-growl-notifications div[data-aid=' + time + ']');
        if (query.length) {
            // could have been dismissed
            $(query).fadeOut();
        }
    }, _alert.timeout || 5000);
}

FT.pages = {
    adminClient : 'Client Management',
    adminUser: 'User Management',
    adminArea: 'Area Management',
    featuresClient: 'Propose Features',
    home: 'Home'
}

FT.logout = function() {
    rest.POST('/api/v1/logout', '')
    .then(function() {
        $('#loginEmail').val('');
        $('#loginPassword').val('');
        FT.loggedUser('');
        FT.breadcrumb([]);
        FT.curPage('login');
        $('#loginEmail').focus();
    })
}

FT.login = {
    message : ko.observable(''),
    click : function() {
        var username = $('#loginEmail').val();
        var passwd = $('#loginPassword').val();
        rest.POST('/api/v1/login', { username: username, passwd: passwd },
                  function(ret) {
                      if (ret.success) {
                          FT.loggedUser(username);
                          FT.curPage('home');
                      } else {
                          // TODO message...
                      }
                  });
    }
}

FT.loggedUser = ko.observable('');
FT.breadcrumb = ko.observableArray([]);

FT.util = {
    ajaxFailFn : function(xhr) {
        if (xhr.status == 409) {
            // validation
            console.log('failed w/ validation or referential integrity errors');
            if (xhr.responseJSON.validationErrors.length > 0) {
                FT.admin.validationErrors(xhr.responseJSON.validationErrors);
            }
        } else {
            // server errors (5xx)
            console.log('server error here');
        }
    }
}

FT.admin = {
    entity: function() {
        // url entity is admin(.*)
        return FT.curPage().substring(5).toLowerCase();
    },

    curEntityId: -1,

    // hackish, alright. Doing it well will require refactoring the grid component
    clientGrid: new PagedGridModel([
                                     { headerText: 'ID', rowText: 'id' },
                                     { headerText: 'Client name', rowText: 'name' },
                                     { headerText: 'Weight', rowText: 'weight' }
                                   ]),

    areaGrid: new PagedGridModel([
                                     { headerText: 'ID', rowText: 'id' },
                                     { headerText: 'Area name', rowText: 'name' }
                                   ]),

    userGrid: new PagedGridModel([
                                     { headerText: 'ID', rowText: 'id' },
                                     { headerText: 'username', rowText: 'username' },
                                     { headerText: 'Full Name', rowText: 'full_name' },
                                     { headerText: 'email', rowText: 'email' },
                                     {
                                         headerText: 'Is Admin?', rowText: function(row) {
                                             return row.is_admin ? '✔' : '';
                                         }
                                     },
                                     { headerText: 'Client', rowText: 'client_name' }
                                   ]),

    updateCurrentGrid: function() {
        var entity = FT.admin.entity();

        // for ALL objects, entities is plural...
        rest.GET('/api/v1/admin/' + entity + 's', function(data) {
            FT.admin[entity + 'Grid'].items(data);
        }).then(function() {
            FT.admin[entity + 'Grid'].vm.currentPageIndex(0);
        });

        if (entity == 'user') {
            // refresh client list
            rest.GET('/api/v1/admin/clients', function(data) {
                FT.admin.clientList(data);
            });
        }
    },

    validationErrors: ko.observableArray([]),

    showAdd: function() {
        var entity = FT.admin.entity();
        container = FT.admin[entity];
        setModelValues(container, emptyObjectFromKnockoutModel(container));

        FT.admin.curEntityId = 0;
        FT.admin.validationErrors([]);
        $('#frm' + entity).modal();
    },

    entityAddOrUpdateFn : function() {
        var entity = FT.admin.entity();
        var jsonData = ko.toJS(FT.admin[entity]);

        var successFn = function(ret, _, xhr) {
            $('#frm' + entity).modal('hide');
            FT.admin.updateCurrentGrid();
        };


        if (FT.admin.curEntityId == 0) {
            // add
            rest.POST('/api/v1/admin/' + entity, jsonData, successFn)
                .fail(FT.util.ajaxFailFn);
        } else {
            // update
            rest.PUT('/api/v1/admin/' + entity + '/' + FT.admin.curEntityId, jsonData, successFn)
                .fail(FT.util.ajaxFailFn);
        }
    },

    // all clients in User admin
    clientList: ko.observableArray(),

    // currently edited admin objects
    client: {
        name: ko.observable(),
        weight: ko.observable()
    },

    user: {
        username: ko.observable(),
        full_name: ko.observable(),
        email: ko.observable(),
        is_admin: ko.observable(false),
        client_id: ko.observable(),
        passwd: ko.observable()
    },

    area: {
        name: ko.observable()
    }
}

// features view
FT.featuresClient = {
    check: function(feature, boo) {
        if (feature.included) {
            // previously was included, so remove it
            FT.featuresClient.postRemoving(feature.id);
        } else {
            FT.featuresClient.postAdding(feature.id);
        }
        FT.featuresClient.query();
        // not doing the `default` action because query() refreshes the controls
    },

    query: function() {
        rest.GET('/api/v1/features', function(ret) {
            FT.featuresClient.own(ret.own);
            FT.featuresClient.others(ret.others);
        });
        $('#ft-features-sortable').sortable({
            handle: '.card-header',
            items: '.card',
            update: function() {
                FT.featuresClient.postOrder();
            }
        });

        // refresh areas also
        rest.GET('/api/v1/admin/areas', function(areas) {
            FT.featuresClient.areaList(areas);
        });
    },

    postOrder: function(options) {
        options = typeof options != 'undefined' ? options : {};
        var order = [];

        $('#ft-features-sortable .card-header').each(function(idx, el) {
            var $el = $(el);
            var feature_id = $el.data('feature-id');
            if (options.remove && options.remove == feature_id) return;

            order.push(feature_id);
        });

        if (options.add) {
            order.push(options.add);
        }

        rest.POST('/api/v1/sort-features', {features : order});
    },

    postAdding: function(which) {
        var opt = { add: which };
        FT.featuresClient.postOrder(opt);
    },

    postRemoving: function(which) {
        var opt = { remove: which };
        FT.featuresClient.postOrder(opt);
    },

    edit: function(feature) {
        rest.GET('/api/v1/feature/' + feature.id, function(data) {
            setModelValues(FT.featuresClient.form, data);
        }).then(function() {
            FT.featuresClient.curEntityId = feature.id;
            FT.admin.validationErrors([]);
            $('#frmfeature').modal();
        });
    },

    add: function() {
        var koObj = FT.featuresClient.form;
        setModelValues(koObj, emptyObjectFromKnockoutModel(koObj));
        FT.featuresClient.curEntityId = 0;
        FT.admin.validationErrors([]);
        $('#frmfeature').modal();
    },

    save: function() {
        var obj = ko.toJS(FT.featuresClient.form);

        if (FT.featuresClient.curEntityId == 0) {
            rest.POST('/api/v1/feature', obj, function() {
                $('#frmfeature').modal('hide');
                FT.featuresClient.query();
            }).fail(FT.util.ajaxFailFn);
        } else {
            rest.PUT('/api/v1/feature/' + FT.featuresClient.curEntityId, obj, function() {
                $('#frmfeature').modal('hide');
                FT.featuresClient.query();
            }).fail(FT.util.ajaxFailFn);
        }
    },

    others : ko.observableArray(),
    own : ko.observableArray(),

    curEntityId: -1,

    form: {
        title : ko.observable(),
        description: ko.observable(),
        is_public: ko.observable(false),
        target_date: ko.observable(),
        url: ko.observable(),
        area_id: ko.observable()
    },

    areaList: ko.observableArray([])
}

ko.applyBindings(FT);
FT.curPage.subscribe(function(val) {
    if (val == 'login') return;

    var breadcrumb = FT.breadcrumb();

    if (breadcrumb.length == 3) {
        breadcrumb = breadcrumb.slice(1);
    }
    breadcrumb.push({page: val, caption: FT.pages[val]});
    FT.breadcrumb(breadcrumb);

    if (val.substring(0, 5) == 'admin') {
        FT.admin.updateCurrentGrid();
    } else if (val == 'featuresClient') {
        FT.featuresClient.query();
    }
});

FT.admin.user.is_admin.subscribe(function(newVal) {
    if (newVal) {
        FT.admin.user.client_id('');
    }
});

// setup bootstrap autofocus for modal windows
[
 ['#frmclient', '#client_name'],
 ['#frmarea', '#area_name'],
 ['#frmuser', '#user_username'],
 ['#frmfeature', '#feature_title']
].forEach(function(pair) {
    $(pair[0]).on('shown.bs.modal', function() {
        $(pair[1]).focus();
    });
});

// if logged in, go to the home
rest.GET('/api/v1/status', function(session) {
    if (session.username) {
        FT.loggedUser(session.username);
        FT.curPage('home');
    }
});

$('#feature_target_date').datepicker({ dateFormat: 'yy-mm-dd' });
