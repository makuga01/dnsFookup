import React, { Component } from "react";
import { Menu, Image, Icon } from "semantic-ui-react";
import {
  BrowserRouter as Router,
  Route,
  Redirect,
  Link
} from "react-router-dom";

class TopBar extends Component {
  constructor(props) {
    super(props);
  }

  state = {
    name: this.props.name,
    redirectHome: false,
    redirectBin: false,
    redirectSettings: false
  };

  render() {
    return (
      <Menu
        stackable
        inverted
      >
        {this.state.redirectHome === true && <Redirect to="/" />}

        <Link
          to="/dashboard"
          onClick={() => this.setState({active:""})}
        >
          <Menu.Item>
            <img src='/bomb_white.png' /> Home
          </Menu.Item>
        </Link>
        <Menu.Item
          name="crt_bin"
          as={Link}
          color='grey'
          active={this.state.active === "dnsbin"}
          to="/dnsbin"
          onClick={() => this.setState({active:"dnsbin"})}
        >
          <Icon inverted name="plus circle" circular />  Create new bin
        </Menu.Item>
        <Menu.Item
          name="bin"
          as={Link}
          color='grey'
          active={this.state.active === "mybins"}
          to="/mybins"
          onClick={() => this.setState({active:"mybins"})}
        >
          <Icon inverted name="database" circular />  My bins
        </Menu.Item>
        <Menu.Item
          name="settings"
          as={Link}
          color='grey'
          active={this.state.active === "settings"}
          to="/settings"
          onClick={() => this.setState({active:"settings"})}
        >

          <Icon inverted name="settings" circular /> Settings
        </Menu.Item>
        <Menu.Item
          name="support"
          as={Link}
          color='grey'
          active={this.state.active === "support"}
          to="/support"
          onClick={() => this.setState({active:"support"})}
        >

          <Icon inverted name="dollar" circular /> Support me ❤️
        </Menu.Item>
        <Menu.Item
          name="logout"
          position="right"
          onClick={this.props.handleLogout}
        >
        <Icon inverted name="log out" circular />  Log Out
        </Menu.Item>
      </Menu>
    );
  }
}
export default TopBar;
