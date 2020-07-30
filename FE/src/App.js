import React, { Component } from "react";
import {
  BrowserRouter as Router,
  Route,
  Redirect,
  Link,
  useHistory
} from "react-router-dom";
import {
  Segment,
  Grid,
  Button,
  Icon
} from "semantic-ui-react";
import "./App.css";
import Home from "./Home";
import Login from "./Login";
import Signup from "./Signup";
import Dashboard from "./Dashboard";
import TopBar from "./TopBar";
import MyBins from "./MyBins";
import NewBin from "./NewBin";
import Settings from "./Settings";
import Support from "./Support";

/* eslint-disable */



class App extends Component {
  state = {
    logged: false,
    name: "",
    redirectSupport:false
  };


  getUser = () => {
    var bearer = "Bearer " + localStorage.getItem("access_token");
    //console.log(bearer);
    var obj = {
      method: "GET",
      headers: new Headers({
        Accept: "aplication/json",
        Authorization: bearer,
        //   "Access-Control-Allow-Origin": "*",
        "Access-Control-Request-Headers": "Authorization, Accept"
      })
    };
    fetch(process.env.REACT_APP_API+"/api/user", obj)
      .then(res => res.json())
      .then(data => {
        if (
          (data.name != null)
        ) {
          this.setUser(data);
          console.log('LoggenIn ok');
        } else if (window.location.pathname != "/") {
          this.handleLogout();
          console.log('HandleLogout');

        }
      })
      .catch(err => {
        if (window.location.pathname != "/") {
          this.handleLogout();
          console.log('HandleLogout');
        }

      });
  };

  setUser = data => {
    this.setState({
      logged: true,
      name: data.name
    });
    console.log(this.state);
  };

  unsetUser = () => {
    this.setState({
      logged: false,
      name: ""
    });
    localStorage.removeItem("access_token");
    window.location = "/"
  };

  componentDidMount() {
    this.getUser();
    this.setState({redirectSupport:false});
  }

  isLogged = () => {
    return this.state.logged;
  };

  handleLogout = event => {
    var bearer = "Bearer " + localStorage.getItem("access_token");
    fetch(process.env.REACT_APP_API+"/auth/logout", {
      method: "POST",
      headers: new Headers({
        Accept: "aplication/json",
        Authorization: bearer
        // 'Content-Type': 'form-data',
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.error === true) {
          console.log("Logout error");
        }
        else {
          this.unsetUser();
        }
      })
      .catch(err => {
        this.unsetUser();
      });
  };

  render() {
    return (
      <div className="App">
        <Router>
          {this.isLogged() && (
            <TopBar
              handleLogout={this.handleLogout}
              unsetUser={this.unsetUser}
            />
          )}
          <Route path="/" exact component={Home} />
          <Route path="/support" component={() => <Support />} />
          {!this.isLogged() && (
            <div>
              <Route
                path="/login"
                component={() => <Login setUser={this.setUser} />}
              />
              <Route
                path="/signup"
                component={() => <Signup setUser={this.setUser} />}
              />
              <Route path="/dashboard" component={() => <Redirect to="/" />} />
            </div>
          )}
          {this.isLogged() && (
            <div>
              <Route path="/" component={() => <Redirect to="/dashboard" />} />
              <Route
                path="/login"
                component={() => <Redirect to="/dashboard" />}
              />
              <Route
                path="/signup"
                component={() => <Redirect to="/dashboard" />}
              />
              <Route
                path="/dashboard"
                component={() => (
                  <Dashboard
                    name={this.state.name}
                    unsetUser={this.unsetUser}
                  />
                )}
              />
              <Route path="/mybins" component={() => <MyBins />} />
              <Route path="/dnsbin" component={() => <NewBin />} />
              <Route path="/settings" component={() => <Settings />} />
            </div>
          )}
          {this.state.redirectSupport === true && <Redirect to="/support" />}
        </Router>
        <Segment
          id='footer'
          inverted
        >
        <Grid
        >
          <Grid.Row>
          <Grid.Column>
            <Button
            inverted
            href="https://github.com/makuga01/dnsFookup"
            target="_blank"
            >
            <Icon
            name='github'
            />Star this project

            </Button>

            <Button
              inverted
              target="_blank"
              href="https://keybase.io/gel0"
            >
              <Icon
                name='envelope outline'
              />
              Any questions/suggestions? Message me!
            </Button>

            <Button
              inverted
              href="https://geleta.eu/whoami"
              target="_blank"
            >
            <Icon
              name='user outline'
            />
              About me
            </Button>

            { !this.state.logged &&
            <Button
              onClick={() => this.setState({redirectSupport:true})}
              inverted
            >
            <Icon
              name='dollar sign'
            />
            Support me ❤️
            </Button>
            }
            {this.state.redirectSupport &&
            <Button
              inverted
              onClick={() => {this.setState({redirectSupport:false});window.location.replace("/");}}
            >
              <Icon name='home'/><Icon name='arrow left'/>
            </Button>}
            </Grid.Column>
          </Grid.Row>
        </Grid>


        </Segment>

      </div>
    );
  }
}

export default App;
