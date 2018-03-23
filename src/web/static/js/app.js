(function(){
    var current_tab = location.hash.replace( /^#!\//, '' );

    var app = angular.module('minion', []);

    app.controller("TabsController", ["$scope", "$location", function($scope, $location) {
        var tabs = this;
        this.availableTabs = ["status", "deploy", "branches", "releases", "settings"];
        this.activeTab = this.availableTabs[0];

        if(current_tab.length) {
            this.activeTab = current_tab;
        }
        else {
            current_tab = this.activeTab;
        }

        $scope.activateTab = function(tab) {
            tabs.activeTab = tab;
            $scope.$emit("tabChanged", tabs.activeTab);
            $scope.$broadcast("tabChanged", tabs.activeTab);
        };

        $scope.isActive = function(tab) {
            return tabs.activeTab === tab;
        };
    }]);

    app.controller("ProjectController", ["$scope", "$http", "projectsService", function($scope, $http, projectsService){
        var ctrler = this;

        this.new_project = {name: "", url: ""};

        this.valid = function() {
            return ctrler.new_project.name.length && ctrler.new_project.url.length;
        }

        this.create = function() {
            $http.post("api/projects/", {name: ctrler.new_project.name, url: ctrler.new_project.url}).then(function(res) {
                console.log("Successfully created", ctrler.new_project.name);
                projectsService.get();
            });
            $('#newProject').modal('hide')
        };
    }]);

    app.service("projectsService", ["$rootScope", "$http", function($rootScope, $http) {
        this.get = function() {
            $rootScope.projects = [];
            $http.get("api/projects/").then(function(response) {
                $rootScope.projects = response.data;
            });
        };
    }]);

    app.directive("projectStatus", function() {
        return {
            restrict: "EA",
            scope: {item: "="},
            templateUrl: "static/html/status.html",
            controllerAs: 'ctrler',
            controller: function($scope, $http, $interval) {
                var ctrler = this;
                var item_id = $scope.item.id;
                this.focused = false;
                this.running = false;
                this.statusURL = "";

                $scope.$on("tabChanged", function(event, args) {
                    if(args === "status") {
                        console.log("status got focus");
                        ctrler.focused = true;
                    }
                    else {
                        console.log("status lost focus");
                        ctrler.focused = false;
                    }
                });

                this.getEndpoint = function() {
                    $http.get("api/projects/" + item_id + "/endpoint/").then(
                        function(res) {
                            ctrler.statusURL = res.data;
                        },
                        function(error) {
                            ctrler.statusURL = "";
                        }
                    );
                };

                this.checkStatus = function() {
                    if(ctrler.focused) {
                        $http.get("api/projects/" + item_id + "/status/").then(function(res) {
                            ctrler.status = res.data;
                            ctrler.running = (ctrler.status === "RUNNING");

                            if(ctrler.running) {
                                ctrler.getEndpoint();
                            }

                            $interval(ctrler.checkStatus, 10000, 1);
                        });
                    }
                    else {
                        $interval(ctrler.checkStatus, 10000, 1);
                    }
                };

                this.changeStatus = function(cmd) {
                    $http.post("api/projects/" + item_id + "/status/", {command: cmd, tag: $scope.item.image}).then(function(res) {
                        console.log(res);
                    });
                };

                this.start = function() {
                    ctrler.changeStatus('start');
                };

                this.stop = function() {
                    ctrler.changeStatus('stop');
                    ctrler.statusURL = "";
                };

                this.restart = function() {
                    ctrler.changeStatus('restart');
                };

                ctrler.checkStatus();
            }
        }
    });

    app.directive("projectSetting", function() {
        return {
            restrict: "EA",
            scope: {item: "="},
            templateUrl: "static/html/settings.html",
            controllerAs: 'ctrler',
            controller: function($scope, $http, projectsService) {
                $scope.project = angular.copy($scope.item);

                ctrler = this;
                $scope.availableProtocols = ["tcp", "udp"];
                $scope.new_port = {host: null, container: null, protocol: null};
                this.new_path = "";

                this.ports_to_delete = [];
                this.ports_to_add = [];

                this.volumes_to_delete = [];
                this.volumes_to_add = [];

                this.ports_modal = "ports-" + $scope.project.name;
                this.volumes_modal = "volumes-" + $scope.project.name;
                this.confirm_modal = "confirm-" + $scope.project.name;

                this.resetNewPort = function() {
                    $scope.new_port = {host: null, container: null, protocol: null};
                }

                this.resetScope = function() {
                    this.ports_to_delete = [];
                    this.ports_to_add = [];
    
                    this.volumes_to_delete = [];
                    this.volumes_to_add = [];

                    $scope.project = angular.copy($scope.item);
                };

                this.deleteProject = function() {
                    $http.delete("api/projects/" + $scope.project.id + "/").then(function(res) {
                        console.log("Successfully deleted", $scope.project.name);
                        projectsService.get();
                    });

                    ctrler.closeModal(ctrler.confirm_modal);
                };
                
                this.openModal = function(name) {
                    ctrler.resetScope();
                    $('#' + name).modal({focus: true});
                };

                this.closeModal = function(name) {
                    $('#' + name).modal('hide');
                    $('.modal-backdrop').remove();
                };

                this.validPort = function() {
                    return $scope.new_port.host > 0 && $scope.new_port.container > 0 && $scope.new_port.protocol;
                };

                this.addPort = function() {
                    ctrler.ports_to_add.push($scope.new_port);
                    ctrler.resetNewPort();
                };

                this.removePort = function(item) {
                    if(item.project) {
                        // this port exists on the DB, schedule to remove it
                        var index = $scope.project.ports.indexOf(item);
                        if (index > -1) {
                            $scope.project.ports.splice(index, 1);
                        }
                        ctrler.ports_to_delete.push(item);
                    }
                    else {
                        // this port was not saved
                        var index = ctrler.ports_to_add.indexOf(item);
                        if (index > -1) {
                            ctrler.ports_to_add.splice(index, 1);
                        }
                    }
                };

                this.savePorts = function() {
                    // first delete ports
                    for(var i = 0; i < ctrler.ports_to_delete.length; i++) {
                        p = ctrler.ports_to_delete[i];
                        $http.delete("api/ports/" + p.host + "/").then(function(res) {
                            console.log("Successfully removed", p.host);
                        });
                    }

                    // then create new ones
                    for(var i = 0; i < ctrler.ports_to_add.length; i++) {
                        p = ctrler.ports_to_add[i];
                        data = {
                            project: $scope.project.id,
                            host: p.host,
                            container: p.container,
                            protocol: p.protocol 
                        }
                        $http.post("api/ports/", data).then(function(res) {
                            console.log("Successfully added", p.host);
                            projectsService.get();
                        });
                    }

                    ctrler.closeModal(ctrler.ports_modal);
                }

                this.addVolume = function() {
                    ctrler.volumes_to_add.push({path: ctrler.new_path});
                    ctrler.new_path = "";
                };

                this.removeVolume = function(item) {
                    if(item.project) {
                        // this volume exists on the DB, schedule to remove it
                        var index = $scope.project.volumes.indexOf(item);
                        if (index > -1) {
                            $scope.project.volumes.splice(index, 1);
                        }
                        ctrler.volumes_to_delete.push(item);
                    }
                    else {
                        // this volume was not saved
                        var index = ctrler.volumes_to_add.indexOf(item);
                        if (index > -1) {
                            ctrler.volumes_to_add.splice(index, 1);
                        }
                    }
                };

                this.saveVolumes = function() {
                    // first delete volumes
                    for(var i = 0; i < ctrler.volumes_to_delete.length; i++) {
                        v = ctrler.volumes_to_delete[i];
                        $http.delete("api/volumes/" + v.id + "/").then(function(res) {
                            console.log("Successfully removed", v.path);
                        });
                    }
                    
                    // then create new ones
                    for(var i = 0; i < ctrler.volumes_to_add.length; i++) {
                        v = ctrler.volumes_to_add[i];
                        data = {
                            project: $scope.project.id,
                            path: v.path
                        }
                        $http.post("api/volumes/", data).then(function(res) {
                            console.log("Successfully added", v.path)
                            projectsService.get();
                        });
                    }

                    ctrler.closeModal(ctrler.volumes_modal);
                }
            } 
        };
    });

    app.directive("projectDeploy", function() {
        return {
            restrict: "EA",
            scope: {item: "="},
            templateUrl: "static/html/deploy.html",
            controller: function($scope, $http) {
                ctrler = this;
                var item_id = $scope.item.id;
                $scope.selectedTag = $scope.item.image;

                $scope.availableTags = [];

                $scope.getTags = function() {
                    $http.get("api/projects/" + item_id + "/tags/").then(function(res) {
                        $scope.availableTags = res.data;
                    });
                };

                $scope.tagChanged = function() {
                    return $scope.selectedTag != $scope.item.image;
                }

                $scope.deploy = function() {
                    $http.post("api/projects/" + item_id + "/deploy/", {tag: $scope.selectedTag}).then(function(data) {
                        console.log(data);
                    })
                };

                $scope.getTags();
            }
        }
    });

    app.directive("projectBuild", function() {
        return {
            restrict: "EA",
            scope: {item: "=", type: "@", param: "@"},
            templateUrl: "static/html/build.html",
            controller: function($scope, $http) {
                ctrler = this;
                var item_id = $scope.item.id;
                $scope.selectedRef = "";
                $scope.availableRefs = [];

                $scope.getRefs = function() {
                    $http.get("api/projects/" + item_id + "/" + $scope.type + "/").then(function(res) {
                        $scope.availableRefs = res.data;
                    });
                };

                $scope.build = function() {
                    params = {};
                    params[$scope.param] = $scope.selectedRef
                    $http.post("api/projects/" + item_id + "/build/", params).then(function(data) {
                        console.log(data);
                    })
                };

                $scope.getRefs();
            }
        }
    });

    app.run(function($rootScope, projectsService) {
        projectsService.get();
    });
})();;
