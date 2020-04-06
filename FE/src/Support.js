import React, { Component } from "react";
import {
  Button,
  Form,
  Grid,
  Header,
  Message,
  Segment,
  Icon,
  Divider,
  Image
} from "semantic-ui-react";
import {CopyToClipboard} from 'react-copy-to-clipboard';

class Support extends Component {
  render() {
    return (
      <div>
  <Grid columns={3} divided>
    <Grid.Row>
    <Grid.Column>
      </Grid.Column>
      <Grid.Column>
        <Segment inverted>
        <Header
          as='h1'
          icon
          textAlign="center"
          inverted
        >
          <Icon
            name="dollar"
            circular
            inverted
          />
          <Header.Content>Like DNSfookup?  Support it!</Header.Content>
          <Header as='h2' inverted>Please donate to help me keep this running</Header>
        </Header>
        <Divider/>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
        <input type="hidden" name="cmd" value="_s-xclick" />
        <input type="hidden" name="hosted_button_id" value="B4EF928AGVUT2" />
        <input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" border="0" name="submit" title="PayPal - The safer, easier way to pay online!" alt="Donate with PayPal button" />
        <img alt="" border="0" src="https://www.paypal.com/en_SK/i/scr/pixel.gif" width="1" height="1" />
        </form>
        <Divider/>
        <Header
          as='h2'
        >
        Bitcoin
        </Header>
        <Image
         src='/btc.png'
         centered
         size='small'
       />
        <CopyToClipboard
          text='3QVnTSt9Y4McFjEC8HjcyCdqeHEsz8ucrQ'
          onCopy={() => {
            this.setState({copied: true});
          }}
        >
          <Button
            size='small'
            color='orange'
            icon
            labelPosition='left'
          >
          <Icon name='copy outline' />
          Copy BTC adress
          </Button>
        </CopyToClipboard>



        </Segment>
      </Grid.Column>
      <Grid.Column>
      <Segment inverted>
      <Header
        as='h1'
        icon
        textAlign="center"
        inverted
      >
      <Header.Content>Hall of Donate fame</Header.Content>
      <Header.Subheader
      inverted
      >
        If you donated and want to appear here - Message me on <a target='_blank' href='https://keybase.io/gel0'>keybase</a>
      </Header.Subheader>
      <Header.Subheader
      inverted
      >
        Or you can get my email <a href='https://geleta.eu/whoami' target='_blank'>here</a>
      </Header.Subheader>
      </Header>
      Notning here so far :( Rich hackers are welcome
      </Segment>
      </Grid.Column>
    </Grid.Row>
  </Grid>
    </div>);
  }
}

export default Support;
