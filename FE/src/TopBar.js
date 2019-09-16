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
      <Menu stackable>
        {this.state.redirectHome === true && <Redirect to="/" />}

        <Link to="/dashboard">
          <Menu.Item>
            <Icon size="big" name="globe" />
          </Menu.Item>
        </Link>
        <Menu.Item name="bin" as={Link} to="/mybins">
          My bins
        </Menu.Item>
        <Menu.Item name="settings" as={Link} to="/settings">
          Settings
        </Menu.Item>
        <Menu.Item name="logout" onClick={this.props.handleLogout}>
          Log Out
        </Menu.Item>
      </Menu>
    );
  }
}
export default TopBar;
