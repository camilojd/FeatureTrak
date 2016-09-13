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
FT.login = {
    message : ko.observable(''),
    click : function() {
        // yada yada
    }
}

FT.breadcrumb = ko.observableArray([['Manage Clients', 'adminClient'], ['Propose features', 'featuresClient']]);

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

        var failFn = function(xhr) {
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
        };

        if (FT.admin.curEntityId == 0) {
            // add
            rest.POST('/api/v1/admin/' + entity, jsonData, successFn)
                .fail(failFn);
        } else {
            // update
            rest.PUT('/api/v1/admin/' + entity + '/' + FT.admin.curEntityId, jsonData, successFn)
                .fail(failFn);
        }
    },

    // all clientes in User admin
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
        is_admin: ko.observable(),
        client_id: ko.observable(),
        passwd: ko.observable()
    },

    area: {
        name: ko.observable()
    }
}


ko.applyBindings(FT);
FT.curPage.subscribe(function(val) {
    if (val.substring(0, 5) == 'admin') {
        FT.admin.updateCurrentGrid();
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
 ['#frmuser', '#user_username']
].forEach(function(pair) {
    $(pair[0]).on('shown.bs.modal', function() {
        $(pair[1]).focus();
    });
});
