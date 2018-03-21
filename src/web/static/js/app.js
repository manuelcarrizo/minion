(function(){
    var current_tab = location.hash.replace( /^#!\//, '' );

    var app = angular.module('minion', []);

    app.controller("TabsController", ["$scope", "$location", function($scope, $location) {
        var tabs = this;
        this.availableTabs = ["status", "deploy", "branches", "releases"];
        this.activeTab = this.availableTabs[0];

        if(current_tab.length) {
            this.activeTab = current_tab;
        }
        else {
            current_tab = this.activeTab;
        }

        $scope.activateTab = function(tab) {
            tabs.activeTab = tab;
        };

        $scope.isActive = function(tab) {
            return tabs.activeTab === tab;
        };
    }]);

    app.service("projectsFactory", ["$http", "$q", function($http, $q) {
        var deferred = $q.defer();

        $http.get("api/projects").then(function(response) {
            deferred.resolve(response.data);
        },
        function(response) {
            deferred.reject(response);
        });

        return deferred.promise;
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
                this.focused = true;
                this.running = false;
                this.statusURL = "";

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
//                            console.log($scope.item.name, 'is', data)
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
                    $http.get("api/projects/" + item_id + "/" + $scope.type).then(function(res) {
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

    app.run(function($rootScope, projectsFactory) {
        projectsFactory.then(function(projects) {
            $rootScope.projects = projects;
        });
    });
})();;
