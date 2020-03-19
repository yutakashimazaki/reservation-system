/*global SpaceBooking _config AmazonCognitoIdentity AWSCognito*/

var SpaceBooking = window.SpaceBooking || {};

(function scopeWrapper($) {
    var signinUrl = '/login';
    var attributeList = [];

    var poolData = {
        UserPoolId: _config.cognito.userPoolId,
        ClientId: _config.cognito.userPoolClientId
    };

    var userPool;

    if (!(_config.cognito.userPoolId &&
          _config.cognito.userPoolClientId &&
          _config.cognito.region)) {
        // $('#noCognitoMessage').show();
        console.log('No Cognito');
        return;
    }

    userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);
    const cognitoUser = userPool.getCurrentUser();

    if (typeof AWSCognito !== 'undefined') {
        AWSCognito.config.region = _config.cognito.region;
    }

    SpaceBooking.signOut = function signOut() {
        userPool.getCurrentUser().signOut();
    };

    // サインアウト
    // SpaceBooking.signOut()

    SpaceBooking.authToken = new Promise(function fetchCurrentAuthToken(resolve, reject) {
        var cognitoUser = userPool.getCurrentUser();
        if (cognitoUser) {
            cognitoUser.getSession(function sessionCallback(err, session) {
                if (err) {
                    reject(err);
                } else if (!session.isValid()) {
                    resolve(null);
                } else {
                    resolve(session.getIdToken().getJwtToken());
                }
            });
        } else {
            // resolve(null);
            window.location.href = '/login';
        }
    });



}(jQuery));
