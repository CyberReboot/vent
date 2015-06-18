#!/usr/bin/perl

# taken originally from a smokeping config generator written by @glewis
# modified to work for getting hostnames and associated ip addresses in dns

use warnings;
use strict;

if($#ARGV != '2') {
  print "Please spcify the domain, domain server, and subnet prefix: \n\n";
  print "  ./list-servers.pl my.domain domain_controller 10.100\n";
  exit(1);
}

my $zone;
my $server;
my $subnet;
my $d;

$zone   = $ARGV[0];
$server = $ARGV[1];
$subnet = $ARGV[2];

$d = fetchzone($zone, $server, $subnet);
gensmokeconfig($d, $zone);

exit(0);

sub gensmokeconfig {

  my $add_ips;
  my $add_subnets;
  my $d;
  my $flag;
  my $i;
  my $j;
  my $longname;
  my $shortname;
  my $status;
  my $zone;
  my @keys;
  my @ips;
  my @subnet_ip;

  $d    = shift;
  $zone = shift;

  $flag = 0;

  my $filename = '/tmp/output.csv';
  open(my $fh, '>', $filename) or die "Could not open file '$filename' $!";
  print $fh "hostname,ip,subnet,additional_ips,additional_subnets\n";

  @keys = sort(keys(%{$d}));
  for($i = 0; $i <= $#keys; $i++) {
    $longname = lc($keys[$i]);
    $shortname = $keys[$i];
    $shortname =~ s/\./\-/g;

    $status = 1;

    # TODO perhaps make this a flag?
    $status = ping($longname);

    if($status) {
      @ips = nslookup($longname);
      print "$longname\n";
      print $fh "$longname,";
      $add_ips = "";
      $add_subnets = "";
      # what if no ip for the hostname?
      for($j = 0; $j <= $#ips; $j++) {
        # add ip andsubnet and additional ips/subnets
        if($j == 0) {
          @subnet_ip = split /\./, $ips[$j];
          print $fh "$ips[$j],$subnet_ip[0].$subnet_ip[1].$subnet_ip[2].0/24,";
        }
        else {
          $flag = 1;
          if($j == 1) {
            if($j == $#ips) {
              @subnet_ip = split /\./, $ips[$j];
              $add_ips = "\"[$ips[$j]]\"";
              $add_subnets = "\"[$subnet_ip[0].$subnet_ip[1].$subnet_ip[2].0/24]\"";
            }
            else {
              @subnet_ip = split /\./, $ips[$j];
              $add_ips = "\"[$ips[$j],";
              $add_subnets = "\"[$subnet_ip[0].$subnet_ip[1].$subnet_ip[2].0/24,";
            }
          }
          elsif($j == $#ips) {
            @subnet_ip = split /\./, $ips[$j];
            $add_ips .= "$ips[$j]]\"";
            $add_subnets .= "$subnet_ip[0].$subnet_ip[1].$subnet_ip[2].0/24]\"";
          }
          else {
            @subnet_ip = split /\./, $ips[$j];
            $add_ips .= "$ips[$j],";
            $add_subnets .= "$subnet_ip[0].$subnet_ip[1].$subnet_ip[2].0/24,";
          }
        }
      }
      print $fh "$add_ips,$add_subnets";
      print $fh "\n";
    }

  }
  close $fh;
  commit($filename);
}

sub commit {

  my $cmd;
  my $file;
  my $out;
  my @file_parts;

  $file = shift;
  @file_parts = split /\//, $file;

  # keep internal
  $cmd = "cd /tmp; git clone git\@github.com:CyberReboot/network-data.git;";
  $out = `$cmd`;
  $cmd = "cd /tmp/network-data; git config user.name \"automated agent\"; git config user.email \"cyberreboot\@iqt.org\";";
  $out = `$cmd`;
  $cmd = "cd /tmp/network-data; mkdir -p dyn_data; cp $file dyn_data/; git add dyn_data/$file_parts[$#file_parts]; git commit -a -m \"update dns records\"; git push origin master;";
  $out = `$cmd`;
}

sub nslookup {

  my $cmd;
  my $host;
  my $i;
  my $out;
  my @address;
  my @lines;
  my @ip;
  my @ips;

  $host = shift;

  @ip = ();
  @ips = ();

  $cmd = "/usr/bin/nslookup $host";
  $out = `$cmd`;

  @lines  = split /\n/, $out;
  for($i = 0; $i <= $#lines; $i++) {
    if($lines[$i] =~ /Address:/i) {
      if($lines[$i] !~ /#53/i) {
        @ip = split /Address: /, $lines[$i];
        push @ips, $ip[1];
      }
    }
  }

  return(sort @ips);
}

sub ping {

  my $cmd;
  my $debug;
  my $host;
  my $out;
  my $status;

  $host = shift;

  $debug = 1;
  $status = 0;

  $cmd = "/bin/ping -c 2 -w 2 $host";
  $out = `$cmd`;

  if($out =~ / bytes from /ms) {
    $status = 1;
  } else {
    #print STDERR "warning, ignoring $host due to lack of ping response\n" if $debug;
  }

  return($status);
}

sub rundig {

  my $cmd;
  my $out;
  my $server;
  my $zone;

  $zone   = shift;
  $server = shift;

  $cmd = "/usr/bin/dig -4 -t axfr \@$server $zone";
  $out = `$cmd`;

  return($out);

}

sub fetchzone {

  my $i;
  my $out;
  my $server;
  my $subnet;
  my $zone;
  my %d;
  my @lines;

  $zone   = shift;
  $server = shift;
  $subnet = shift;

  $out = rundig($zone, $server);
  while($out !~ /Query time:/m) {
    print STDERR "Sleeping 3 seconds to try dig again, transfer failed...\n";
    print STDERR $out;
    sleep 3;
    $out = rundig($zone, $server);
  }

  @lines = split(/\n/, $out);
  for($i = 0; $i <= $#lines; $i++) {
    $lines[$i] = uc($lines[$i]);
    # check subnet - should be improved
    if($lines[$i] =~ /\s$subnet/) {
      $lines[$i] =~ s/\.?\s.*//; # strip off the extra fields...
      if($lines[$i] !~ /^_|^;|DCWDS|FORESTDNSZONES|DOMAINDNSZONES|^DEL/i
          && $lines[$i] !~ /^\s*$/
          && $lines[$i] ne uc($zone)) {
        $d{$lines[$i]} = 1;
      };
    }
  }

  return(\%d);

}
