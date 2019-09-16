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

        <Header size="huge" icon textAlign="center">
          <Icon name="globe" circular />
          <Header.Content>DNSfookup</Header.Content>
          <Header.Subheader>DNS rebinding... Just way better!</Header.Subheader>
        </Header>
        <Grid centered>
          <Grid.Row columns={1}>
            <Link to="/login">
              <Button big primary>
                Log In
              </Button>
            </Link>
            <Link to="/signup">
              <Button big secondary>
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
