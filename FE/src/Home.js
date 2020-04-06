import React, { Component } from "react";
import { Grid, Button, Header, Icon } from "semantic-ui-react";
import { Link } from "react-router-dom";

class Home extends Component {
  render() {
    return (
      <div>
        <Grid centered>
          <Grid.Row />
          <Grid.Row />
          <Grid.Row />
          <Grid.Row />
          <Grid.Row />
          <Grid.Row />
        </Grid>

        <Header
          size="huge"
          icon
          textAlign="center"
          inverted
        >
          <Icon
            name="globe"
            circular
            inverted
          />
          <Header.Content>DNSfookup</Header.Content>
          <Header.Subheader>DNS that fucks things up</Header.Subheader>
        </Header>
        <Grid centered>
          <Grid.Row columns={1}>
            <Link to="/login">
              <Button big primary inverted>
                Log In
              </Button>
            </Link>
            <Link to="/signup">
              <Button big inverted>
                Sign Up
              </Button>
            </Link>
          </Grid.Row>
        </Grid>
      </div>
    );
  }
}

export default Home;
