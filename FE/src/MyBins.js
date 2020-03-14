import React, { Component } from "react";
import {
  Grid,
  Dropdown,
  Header,
  Icon,
  Divider,
  Table,
  Menu,
  Label,
  Button
} from "semantic-ui-react";
import { Link } from "react-router-dom";
import {CopyToClipboard} from 'react-copy-to-clipboard';

class MyBins extends Component {
  state = {
    selected: "",
    bins: [],
    logs: []
  };

  getBins = () => {
    var bearer = "Bearer " + localStorage.getItem("access_token");
    var obj = {
      method: "GET",
      headers: new Headers({
        Accept: "aplication/json",
        Authorization: bearer,
        "Access-Control-Request-Headers": "Authorization, Accept"
      })
    };
    fetch("http://localhost:5000/api/fookup/listAll", obj)
      .then(res => res.json())
      .then(data => {
        if (
          (data.msg !== "Token has expired") &
          (data.msg !== "Not enough segments")
        ) {
          this.setState({
            bins: data.reverse().map(bin => ({
              value: bin.uuid,
              text: bin.name
            }))
          });
        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  getLogs = uuid => {
    var bearer = "Bearer " + localStorage.getItem("access_token");
    event.preventDefault();
    var data = new FormData();
    data.append("uuid", uuid);
    var obj = {
      method: "POST",
      headers: new Headers({
        Accept: "aplication/json",
        Authorization: bearer,
        //   "Access-Control-Allow-Origin": "*",
        "Access-Control-Request-Headers": "Authorization, Accept"
      }),
      body: data
    };
    fetch("http://localhost:5000/api/fookup/logs/uuid", obj)
      .then(res => res.json())
      .then(data => {
        if (
          (data.msg !== "Token has expired") &
          (data.msg !== "Not enough segments")
        ) {
          this.setState({
            logs: data.reverse()
          });
          console.log(data);
        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  deleteUUID = () => {
    var bearer = "Bearer " + localStorage.getItem("access_token");
    event.preventDefault();
    var uuid = this.state.selected
    var data = new FormData();
    data.append("uuid", uuid);
    var obj = {
      method: "POST",
      headers: new Headers({
        Accept: "aplication/json",
        Authorization: bearer,
        //   "Access-Control-Allow-Origin": "*",
        "Access-Control-Request-Headers": "Authorization, Accept"
      }),
      body: data
    };
    fetch("http://localhost:5000/api/fookup/delete", obj)
      .then(res => res.json())
      .then(data => {
        if (data.success === true) {
          this.setState({
            selected: ""
          });
          this.getBins();

        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  componentDidMount() {
    this.getBins();
  }
  onChange = (e, data) => {
    this.setState({ selected: data.value });
    this.getLogs(data.value);
  };

  handleReload = () => {
    this.getLogs(this.state.selected);
  };

  logsTable(input_data) {
    return (
      <Table celled loading>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell>Resolved to</Table.HeaderCell>
            <Table.HeaderCell>Domain requested</Table.HeaderCell>
            <Table.HeaderCell>Origin ip:port</Table.HeaderCell>
            <Table.HeaderCell>Time</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {input_data.map(log => (
            <Table.Row>
              <Table.Cell>{log.resolved_to}</Table.Cell>
              <Table.Cell>{log.domain}</Table.Cell>
              <Table.Cell>
                {log.origin_ip}:{log.port}
              </Table.Cell>
              <Table.Cell>{log.created_date}</Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>
    );
  }
  render() {
    return (
      <div>
        <Grid textAlign="center" style={{ height: "25vh" }}>
          <Grid.Row>
            <Grid.Column width={3}>
              <Dropdown
                placeholder="Select dns bin"
                search
                selection
                onChange={this.onChange}
                options={this.state.bins}
              />
              <br/>
              <br/>
              {this.state.selected !== "" &&
              (
                <Button.Group vertical>
                <Button
                width={2}
                onClick={this.deleteUUID}
                icon='trash alternate'
                labelPosition='left'
                color='red'
                content='Delete this bin'
                  >
                </Button>
                      <CopyToClipboard
                      text={this.state.selected+".gel0.space"}
                      onCopy={() => this.setState({copied: true})}
                      >
                      <Button
                      icon='copy outline'
                      labelPosition='left'
                      content='Copy domain name'
                      color='yellow'
                        >
                      </Button>
                      </CopyToClipboard>

                  </Button.Group>
                    )
            }
            </Grid.Column>
            <Grid.Column width={10}>
              {this.state.selected === "" && (
                <Header size="huge" icon textAlign="center">
                  <Icon name="shuffle" />
                  <Header.Content>My DNSfookup bins</Header.Content>
                  <Header.Subheader>
                    Select name of your bin and view logs!
                  </Header.Subheader>
                </Header>
              )}
              {this.state.selected !== "" && this.logsTable(this.state.logs)}
            </Grid.Column>
            <Grid.Column width={1}>
              <Button circular icon="redo" onClick={this.handleReload} />
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </div>
    );
  }
}

export default MyBins;
