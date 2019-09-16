import React, { Component } from "react";
import {
  Button,
  Form,
  Grid,
  Header,
  Message,
  Segment,
  Icon
} from "semantic-ui-react";
import {
  BrowserRouter as Router,
  Route,
  Link,
  Redirect
} from "react-router-dom";

class Signup extends Component {
  constructor(props) {
    super(props);
  }

  state = {
    loginError: false
  };

  signupErr = x => {
    this.setState({
      signupError: true,
      errMessage: x.message
    });
    console.log(this.state);
  };
  postSignup = event => {
    event.preventDefault();

    let email = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    var data = new FormData();
    data.append("username", email);
    data.append("password", password);

    fetch("http://localhost:5000/auth/signup", {
      method: "POST",
      headers: new Headers({
        // 'Content-Type': 'form-data',
      }),
      body: data
    })
      .then(res => res.json())
      .then(data => {
        if (data.error != null) {
          this.signupErr(data);
        } else {
          localStorage.setItem("access_token", data.access_token);
          this.props.setUser(data);
        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  SignupForm() {
    return (
      <Grid
        textAlign="center"
        style={{ height: "100vh" }}
        verticalAlign="middle"
      >
        <Grid.Column style={{ maxWidth: 450 }}>
          <Header as="h2" color="black" textAlign="center">
            Create new account!
          </Header>
          <Form size="large" id="signupForm">
            {this.state.signupError && (
              <Message icon color="red">
                <Icon name="ban" />
                {this.state.errMessage}
              </Message>
            )}
            <Segment stacked>
              <Form.Input
                fluid
                icon="user"
                iconPosition="left"
                placeholder="Username"
                id="username"
              />
              <Form.Input
                fluid
                icon="lock"
                iconPosition="left"
                placeholder="Password"
                type="password"
                id="password"
              />

              <Button secondary onClick={this.postSignup} fluid size="large">
                Sign up
              </Button>
              <br />
              <Grid>
                <Grid.Column>
                  <Link to="/login">
                    <Button primary style={{ maxWidth: 300 }} size="medium">
                      Log in
                    </Button>
                  </Link>
                </Grid.Column>
              </Grid>
            </Segment>
          </Form>
        </Grid.Column>
      </Grid>
    );
  }

  render() {
    return <div>{this.SignupForm()}</div>;
  }
}

export default Signup;
