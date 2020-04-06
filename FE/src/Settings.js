import React, { Component } from "react";
import {
  Grid,
  Button,
  Header,
  Icon,
  Form,
  Input,
  Segment,
  Message,
  Popup
} from "semantic-ui-react";
import { Link } from "react-router-dom";
import {CopyToClipboard} from 'react-copy-to-clipboard';

class Settings extends Component {

  state = {
    active: "settings",
    copied: false,
    pw_changed: false,
    pw_fail: false,
    fail_msg: "",
    del_msg: "",
    del_fail: false
  }


  deletMe = () => {
    event.preventDefault();

    let pw = document.getElementById("delete_pw").value;
    if (pw == ""){
      this.setState({
        del_fail: true,
        del_msg: 'Fill the password in'
      });
      setTimeout(() => this.setState({pw_fail:false}), 2000);
      return
    } else if (pw.length < 8){
      this.setState({
        del_fail: true,
        del_msg: 'Minimum password length is 8 characters.. Did you know that?'
      });
      setTimeout(() => this.setState({pw_fail:false}), 2000);
      return
    }

    var data = {
      "password": pw,
    }
    var bearer = "Bearer " + localStorage.getItem("access_token");

    fetch("http://rbnd.gl0.eu:5000/auth/delete_me", {
      method: "POST",
      Accept: "aplication/json",
      headers: new Headers({
        'Authorization': bearer,
        'Content-Type': 'application/json',
        "Access-Control-Request-Headers": "Authorization, Accept"
      }),
      body: JSON.stringify(data)
    })
      .then(res => res.json())
      .then(data => {
        if (data.success === true) {
          localStorage.getItem("access_token");
          window.location.reload();
        } else {
          this.setState({
            del_fail: true,
            del_msg: data.message
          });
          setTimeout(() => this.setState({del_fail:false}), 1420);

        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  pwChange = () => {
    event.preventDefault();

    let oldpw = document.getElementById("oldpw").value;
    let newpw = document.getElementById("newpw").value;
    if (oldpw == "" || newpw == ""){
      this.setState({
        pw_fail: true,
        fail_msg: 'Please fill out both fields'
      });
      setTimeout(() => this.setState({pw_fail:false}), 2000);
      return
    } else if (oldpw.length < 8 || newpw.length < 8){
      this.setState({
        pw_fail: true,
        fail_msg: 'Minimum password length is 8 characters'
      });
      setTimeout(() => this.setState({pw_fail:false}), 2000);
      return
    } else if (oldpw===newpw){
      this.setState({
        pw_fail: true,
        fail_msg: 'For real?'
      });
      setTimeout(() => this.setState({pw_fail:false}), 2000);
      return
    }

    var data = {
      "old_password": oldpw,
      "new_password": newpw
    }
    var bearer = "Bearer " + localStorage.getItem("access_token");

    fetch("http://rbnd.gl0.eu:5000/auth/change_pw", {
      method: "POST",
      Accept: "aplication/json",
      headers: new Headers({
        'Authorization': bearer,
        'Content-Type': 'application/json',
        "Access-Control-Request-Headers": "Authorization, Accept"
      }),
      body: JSON.stringify(data)
    })
      .then(res => res.json())
      .then(data => {
        if (data.success === true) {
          this.setState({
            pw_changed: true,
            pw_fail: false
          });
          setTimeout(() => this.setState({pw_changed:false}), 1420);

        } else {
          this.setState({
            pw_fail: true,
            fail_msg: data.message
          });
          setTimeout(() => this.setState({pw_fail:false}), 1420);

        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  render() {
    return (
      <div>

        <Header
          size="huge"
          icon
          textAlign="center"
          inverted
        >
          <Icon
            name="settings"
            circular
            inverted
          />
        </Header>
        <Grid centered>
            <Grid.Row>
            <Segment inverted>
            <Form
              inverted
            >
            <Header
              as="h2"
              inverted
            >
              Change password
            </Header>
              <Form.Group widths='equal'>
                <Form.Field
                  control={Input}
                  id='oldpw'
                  label='Old password'
                  placeholder='password'
                  type="password"
                />
                <Form.Field
                  control={Input}
                  id='newpw'
                  label='New password'
                  placeholder='Passw0rd123'
                  type="password"
                />
                </Form.Group>
              <Form.Field
                control={Button}
                inverted
                onClick={this.pwChange}
                primary
              >
                Submit
              </Form.Field>
            </Form>
            <Message
              hidden={!this.state.pw_changed}
              positive
            >
              <Message.Header>Password changed!</Message.Header>
            </Message>
            <Message
              hidden={!this.state.pw_fail}
              negative
            >
              <Message.Header>{this.state.fail_msg}</Message.Header>
            </Message>
            </Segment>
          </Grid.Row>

          <Grid.Row>
            <Message
              color='black'
              hidden={!this.state.copied}
              content='Copied!'
            />
          </Grid.Row>
          <Grid.Row>
            <CopyToClipboard
              text={localStorage.getItem('access_token')}
              onCopy={() => {
                this.setState({copied: true});
                setTimeout(() => this.setState({copied:false}), 800);
              }}
            >
              <Button
                size='huge'
                color='olive'
                icon
                labelPosition='left'
              >
              <Icon name='copy outline' />
              Copy my JWT token
              </Button>
            </CopyToClipboard>

          </Grid.Row>

          <Grid.Row>

          <Popup
            inverted
            on='click'
            header='You sure wanna do this?'
            trigger={
              <Button
                size='huge'
                color='red'
                icon
                labelPosition='left'
              >
              <Icon name='erase' />
              Erase all my data from here
              </Button>
            }
            content={
              <Segment
                inverted
              >
                <Form inverted>
                  <Form.Group>
                    <Form.Field
                      control={Input}
                      id='delete_pw'
                      label='Your password'
                      placeholder='S00nDedPassw0rd'
                      type="password"
                    />
                  </Form.Group>
                <Form.Field
                  control={Button}
                  color='red'
                  inverted
                  onClick={this.deletMe}
                >
                  Delete me forever!
                </Form.Field>

                </Form>
                <Segment
                  hidden={!this.state.del_fail}
                  color='red'
                  inverted
                >
                  <Header
                    as='h5'
                  >
                  {this.state.del_msg}
                  </Header>
                </Segment>
              </Segment>
            }
          />

          </Grid.Row>
        </Grid>
      </div>
    );
  }
}

export default Settings;
